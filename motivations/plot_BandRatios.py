"""
Band Ratio Measures
===================

Exploring band ratio measures in the context of the FOOOF model.
"""

###################################################################################################
#
# Band Ratios Project
# -------------------
#
# Note: this example is quick demonstration of how band ratios measures relate
# to periodic and aperiodic activity.
#
# This topic has been the topic of a full research project, available
# `here <https://github.com/voytekresearch/BandRatios>`_,
#

###################################################################################################
#
# Introduction
# ------------
#
# Band ratios measures are a relatively common measure, proposed to measure oscillatory,
# or periodic, activity.
#
# They are typically calculated as:
#
# .. math::
#    BR = \frac{avg(low band power)}{avg(high band power)}
#
# In this notebook we will explore this measure in the context of conceptualizing
# neural power spectra as a combination of both aperiodic and periodic activity.
#

###################################################################################################

from fooof.sim import gen_power_spectrum

from fooof.plts import plot_spectrum_shading

from fooof.utils import trim_spectrum

from fooof.bands import Bands

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

# Simulation Settings
nlv = 0
f_res = 0.5
f_range = [3, 30]

# Set our band definitions
bands = Bands({'theta' : [4, 8], 'alpha' : [8, 13], 'beta' : [13, 30]})

###################################################################################################

# Simulate a power spectrum
freqs, pows = gen_power_spectrum(f_range, [0, 1.5], [[10, 0.31, 1],
                                 [22, 0.2, 2]], nlv=nlv, freq_res=f_res)

###################################################################################################

#


###################################################################################################

# Calculate a band ratio measure
tbr = calc_band_ratio(freqs, pows, bands.theta, bands.beta)
print('Calculate theta / beta ratio is :\t {:1.2f}'.format(tbr))

###################################################################################################

###################################################################################################

###################################################################################################

###################################################################################################

###################################################################################################
