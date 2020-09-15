# ImageVue Server

A flask-socketio based server for providing data from within the EuXFEL data saving system. It utilizes the extra_data module in order to access data directly by giving an instrument number and a run number.

# Maintainer

Clemens Prescher (clemens.prescher@gmail.com)

# Requirements

  - python 3
  - extra_data
  - flask
  - flask-socketio
  - numpy


# Usage

## Starting the server

Run the server by just starting the run script with the wanted port as an argument:

```
python run.py 5566
```

## Connecting a client and receive data

 The payloads for the server are either json objects/dictionaries or just a string/number in case only one parameter is needed
 The server has the following socket commands, with the parameters given in parenthesis:

  - "open_run", ({proposal: 2292, run: 300})
    - opens run 300 from proposal 2292 
    - returns a list of available instrument sources
  - "instrument_sources"
    - returns the available instrument sources from the currently loaded run
  - "keys_for_source", (source)
    - returns a list of available keys for the specified source
  - "read_data", ({source: ..., key: ...})
    - reads the data for a spefic source and key
    - returns the first element of the run
    - the numpy array is converted into a bytearray and can be read in python by np.load(bytearray), for other languages an extra conversion needs to be performed
  - "get_frame", (index)
    - returns the requested frame of the previously read data
    - the numpy array is converted into a bytearray and can be read in python by np.load(bytearray), for other languages an extra conversion needs to be performed

Currently, the server will create a session for each new connection in order to be able to cache the image data, reading image data only on demand would be slower, but might be more beneficial for very large runs.
