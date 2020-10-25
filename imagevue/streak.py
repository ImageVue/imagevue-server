from .server import sio, get_session, request
import numpy as np
from scipy.optimize import curve_fit
import tifffile as tiff

import os

module_path = os.path.dirname(__file__)
calibration_path = os.path.join(module_path, '..', "data", "streak_calibration")
background_path = os.path.join(module_path, '..', "data", "streak_background")
streak_files = [name for name in os.listdir(calibration_path) if name.endswith('.tif')]
bkg_files = [name for name in os.listdir(background_path) if name.endswith('.tif')]


@sio.on("fit_streak_image")
def fit_streak_image(data):
    with get_session(request.sid, lock=False) as session:
        img_index = data['index']
        img_data = session['data'][img_index]
        x_range = data['x_range']
        y_range = data['y_range']
        x_bin = data['x_bin']
        y_bin = data['y_bin']

        temp, temp_errs, spectra, fitted_spectra = fit_temperature(
            img_data, x_range, y_range, x_bin, y_bin
        )
        return temp


@sio.on("get_streak_calibrations")
def get_streak_calibrations():
    return streak_files

@sio.on("get_streak_backgrounds")
def get_streak_backgrounds():
    return bkg_files

img_x_wavelength = np.linspace(440, 955, 672)


def black_body_function(wavelength, temp, scaling=1):
    wavelength = np.array(wavelength) * 1e-9
    c1 = 3.7418e-16
    c2 = 0.014388
    return scaling * c1 * wavelength ** -5 /  (np.exp(c2 / (wavelength * temp)) - 1)


def fit_temperature(data, x_range=(180, 410), y_range=(0, 508), x_bin=1, y_bin=10):
    out_params = []
    out_errors = []
    spectra = []
    fitted_spectra = []

    wavelength = img_x_wavelength[x_range[0]:x_range[1]]

    for ind in np.arange(y_range[0], y_range[1], y_bin):
        spectrum_y = np.sum(data[ind:ind+y_bin, x_range[0]:x_range[1]], axis=0)
        if x_bin > 1:
            wavelength = img_x_wavelength[x_range[0]:x_raange[1]]
            wavelength, spectrum_y = rebin(wavelength, spectrum_y, x_bin)
        param, cov = curve_fit(black_body_function, wavelength, spectrum_y, 
                               p0=[5000, 1e3])
        
        out_params.append(param)
        out_errors.append(np.sqrt(np.diag(cov)))
        spectra.append((wavelength, spectrum_y))
        fitted_spectra.append((wavelength, 
                               black_body_function(wavelength, *param)))

    return np.array(out_params), np.array(out_errors), spectra, fitted_spectra


def rebin(x, y, bin_size):
    """
    Returns a new pattern which is a rebinned version of the current one.
    """
    x_min = np.round(np.min(x) / bin_size) * bin_size
    x_max = np.round(np.max(x) / bin_size) * bin_size
    new_x = np.arange(x_min, x_max + 0.1 * bin_size, bin_size)

    bins = np.hstack((x_min - bin_size * 0.5, new_x + bin_size * 0.5))
    new_y = (np.histogram(x, bins, weights=y)[0] / np.histogram(x, bins)[0])

    return new_x, new_y