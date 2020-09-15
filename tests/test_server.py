import unittest
from flask_socketio import SocketIOTestClient

from imagevue.server import app, sio


class ServerTests(unittest.TestCase):
    def setUp(self):
        self.client = sio.test_client(app)

    def test_open_run(self):
        result = self.client.emit('open_run', {'proposal': 2292, 'run':262})
        sources = self.client.emit('instrument_sources', callback=True)
        self.assertGreater(len(sources), 0)

    def test_instrument_sources(self):
        result = self.client.emit('open_run', {'proposal': 2292, 'run':262})
        sources = self.client.emit('instrument_sources', callback=True)
        self.assertGreater(len(sources), 0)

    def test_keys_for_source(self):
        result = self.client.emit('open_run', {'proposal': 2292, 'run':262})
        keys = self.client.emit('keys_for_source', 'HED_EXP_VAREX/CAM/2:daqOutput', callback=True)
        self.assertGreater(len(keys), 0)

    def test_read_data(self):
        sources = self.client.emit('open_run', {'proposal': 2292, 'run':262}, callback=True)
        keys = self.client.emit('keys_for_source', 'HED_EXP_VAREX/CAM/2:daqOutput', callback=True)
        data = self.client.emit(
            'read_data', 
            {'source': 'HED_EXP_VAREX/CAM/2:daqOutput', 
             'key': 'data.image.pixels',
             })

    def test_get_frame(self):
        sources = self.client.emit('open_run', {'proposal': 2292, 'run':262}, callback=True)
        keys = self.client.emit('keys_for_source', 'HED_EXP_VAREX/CAM/2:daqOutput', callback=True)
        self.client.emit(
            'read_data', 
            {'source': 'HED_EXP_VAREX/CAM/2:daqOutput', 
             'key': 'data.image.pixels',
             })
        data = self.client.emit('get_frame', 12, callback=True)
        self.assertGreater(len(data), 0)

    def test_train_ids(self):
        result = self.client.emit('open_run', {'proposal': 2292, 'run':262})
        result = self.client.emit('train_ids', 'HED_EXP_VAREX/CAM/2:daqOutput', callback=True)
        self.assertEqual(len(result), 41)