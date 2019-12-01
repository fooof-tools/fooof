"""
Band Ratio Measures
===================

Showing why band ratio measures are bad.
"""

###################################################################################################
#
# Band ratios measures are a
#
# In this notebook
#
# This topic is the
#

###################################################################################################

from fooof.sim import gen_power_spectrum

from fooof.plts import plot_spectrum_shading

from fooof.utils import trim_spectrum

###################################################################################################

# Simulation Settings
nlv = 0
f_res = 0.5
f_range = [3, 30]

###################################################################################################

def calc_band_ratio(freqs, powers, low_band, high_band):
    """Helper function to calculate band ratio measures."""

    # Extract frequencies within each specified band
    _, low_band = trim_spectrum(freqs, powers, low_band)
    _, high_band = trim_spectrum(freqs, powers, high_band)

    # Calculate average power within each band, and then the ratio between them
    ratio = np.mean(low_band) / np.mean(high_band)

    return ratio

###################################################################################################

fs, ps = gen_power_spectrum(f_range, [0, 1.5], [[10, 0.31, 1], [22, 0.2, 2]], nlv=nlv, freq_res=f_res)

###################################################################################################

###################################################################################################
