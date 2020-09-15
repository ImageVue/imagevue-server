import io
from flask import Flask, render_template, request
from flask_socketio import SocketIO
import time

import numpy as np

from extra_data import open_run

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
sio = SocketIO(app, cors_allowed_origins="*")



####################
# Session Handling:
# we currently lock the session when one event is e.g. reading from disk
# subsequent requests have to wait until the previous request is done.
# maybe a wait list is also necessary here, to be able to have each request
# answer in the same order as they came in...
##################

sessions = {}
locked_sessions = []

def get_session(sid, lock=True):
    if sid not in sessions:
        sessions[sid] = {}
    
    class _session_context_manager(object):
        def __init__(self, sid, lock):
            self.sid = sid
            self.session = sessions[sid]
            self.lock = lock
        
        def __enter__(self):
            while(sid in locked_sessions):
                time.sleep(0.001)
            if(self.lock):
                locked_sessions.append(sid)
            return self.session

        def __exit__(self, type, value, traceback):
            if(self.lock):
                del locked_sessions[locked_sessions.index(sid)]
    
    return _session_context_manager(sid, lock)



@sio.on('connect')
def connect():
    sessions[request.sid] = {}

@sio.on('disconnect')
def disconnect():
    del sessions[request.sid]


@sio.on('open_run')
def open_xfel_run(data):
    with get_session(request.sid) as session:
        session['proposal'] = data['proposal']
        session['run_number'] = data['run']
        session['run'] = open_run(proposal=data['proposal'], run=data['run'])

    print("run opened succesfully")

    return list(session['run'].instrument_sources)

@sio.on('instrument_sources')
def instrument_sources():
    with get_session(request.sid) as session:
        return list(session['run'].instrument_sources)


@sio.on('keys_for_source')
def keys_for_source(source):
    with get_session(request.sid) as session:
        return list(session['run'].keys_for_source(source))


@sio.on('read_data')
def read_data(data):
    with get_session(request.sid) as session:
        session['data'] = session['run'].get_array(data['source'], data['key'])
        return convert_array_to_bytes(session['data'][0]);

@sio.on('train_ids')
def train_ids(source):
    with get_session(request.sid) as session:
        return np.array(session['run'].get_array(source, 'data.trainId')).tolist()

@sio.on('get_frame')
def get_frame(index):
    with get_session(request.sid, lock=False) as session:
        return convert_array_to_bytes(session['data'][index])


def convert_array_to_bytes(numpy_array):
    bytestream = io.BytesIO()
    np.save(bytestream, numpy_array)
    return bytestream.getvalue()

def start_server(port):
    sio.run(app, port=port)