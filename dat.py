# helper functions
import numpy as np
from scipy import signal
import foof_utils as fu


def data_syn(filename, freq_range):
#     filename = '6.npy'
#     freq_range = [3, 50]
    psd_array = np.load(filename)
    psd_array = np.log10(psd_array)

    range_size = (np.size(range(freq_range[1]))-0.5)-(np.size(range(freq_range[0]))-1.5)
    xf = np.linspace(freq_range[0], freq_range[1], range_size)

    return psd_array,xf

def data_eeg(filename, freq_range):
#     filename = 'g1025_ch07_raw.npy'
#     freq_range = [0, 50]
    psd_array = np.load(filename)
    psd_array = np.log10(psd_array)

    range_size = np.size(range(freq_range[1]))-np.size(range(freq_range[0]))
    xf = np.linspace(freq_range[0], freq_range[1], range_size)

    psd_array = psd_array.T

    return psd_array,xf

def data_ecog(filename, srate, channel):
#     filename = 'ecog_data.csv'
#     srate = 1000.0
    chandat = np.loadtxt(filename, delimiter=",")
    if np.shape(chandat)[0]<np.shape(chandat)[1]:
        chandat = chandat.T
    chandat = chandat[:, channel]

    # make the PSD
    window_size = int(srate*5)
    overlap = int(window_size * 0.5)

    xf, _, psd_array = signal.spectrogram(chandat, fs=srate, window=('hanning'), nperseg=window_size, noverlap=overlap)
    psd_array = np.log10(psd_array)

    return psd_array,xf

def data_synthesize(freq_range, freq_points, slope_params, oscillation_params, noise_params, n_samples):
    # simulate spectrum as opposed to using real data
    xf = np.linspace(freq_range[0], freq_range[1], freq_points)

    psd_array = fu.simulate_neural_spectra(xf, slope_params, oscillation_params, noise_params)

    for i in range(n_samples-1):
        simulated_spectrum = fu.simulate_neural_spectra(xf, slope_params, oscillation_params, noise_params)
        psd_array = np.vstack((psd_array, simulated_spectrum))

    psd_array = psd_array.T

    return psd_array,xf