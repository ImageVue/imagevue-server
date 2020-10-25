import unittest
from flask_socketio import SocketIOTestClient

from imagevue.server import app, sio

class StreakTests(unittest.TestCase):
    def setUp(self):
        self.client = sio.test_client(app)

    def test_temperature_fitting(self):
        sources = self.client.emit('open_run', {'proposal': 2292, 'run':262}, callback=True)
        keys = self.client.emit('keys_for_source', 'HED/EXP/HAM_STREAK_CAMERA:daqOutput', callback=True)
        data = self.client.emit(
            'read_data', 
            {'source': 'HED/EXP/HAM_STREAK_CAMERA:daqOutput', 
             'key': 'data.image.pixels',
             })
        
        data = {
            "index": 0,
            "x_range": (180, 410),
            "y_range": (0, 508), 
            "x_bin": 1, 
            "y_bin": 10
        }
        result = self.client.emit("fit_streak_image", data, callback=True)
        self.assertGreater(len(result), 0)

    def test_get_calibrations(self):
        calibrations = self.client.emit('get_streak_calibrations', callback=True)
        self.assertGreater(len(calibrations), 0)

    def test_get_bkg(self):
        bkg_files = self.client.emit('get_streak_backgrounds', callback=True)
        self.assertGreater(len(bkg_files), 0)

    