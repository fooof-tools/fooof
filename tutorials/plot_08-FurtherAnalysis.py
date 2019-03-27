"""
08: Further Analysis
====================

Analyze results from fitting FOOOF models.
"""

###################################################################################################
# Exploring FOOOF Analyses
# ------------------------
#
# FOOOF is a method to extract features of interest from your data.
#
# These features can then be examined across or between groups of interest,
# or perhaps fed into further analysis.
#
# Largely, it is up to you what to do after running FOOOF,
# and depends on your questions of interest.
#
# Here, we briefly introduce some analysis utilities that are packaged with FOOOF,
# and explore some simple analyses that can be done with FOOOF outputs.
#

###################################################################################################

# General imports
import numpy as np

# Import FOOOF objects & sim utilities
from fooof import FOOOF, FOOOFGroup
from fooof.sim.params import param_sampler
from fooof.sim.gen import gen_group_power_spectra

# FOOOF comes with some basic analysis function to work with FOOOF outputs
from fooof.analysis import get_band_peak, get_band_peak_group

###################################################################################################

# Load some data
freqs = np.load('dat/freqs.npy')
spectrum = np.load('dat/spectrum.npy')

###################################################################################################

# Fit a FOOOF to explore
fm = FOOOF(peak_width_limits=[2, 8])
fm.fit(freqs, spectrum, [3, 30])

###################################################################################################
# FOOOF Analysis Utilities
# ------------------------
#
# FOOOF is packaged with minimal analysis utility functions.
#
# The plan is for the FOOOF module to stay this way, as supporting further analysis of
# FOOOF-derived results is largely outside the scope of the current module.
#
# Here we only directly include and demonstrate utility functions covering very general use cases.
#
# In particular, we include some utilities that are useful for parsing peak results,
# and extracting peaks from frequency ranges of interest.

###################################################################################################
# Analyzing Band-Specific Oscillations
# ------------------------------------
#

###################################################################################################

# Set up indexes for accessing data, for convenience
cf_ind, pw_ind, bw_ind = 0, 1, 2

# Define frequency bands of interest
theta_band = [4, 8]
alpha_band = [8, 12]
beta_band = [15, 30]

###################################################################################################
# get_band_peak
# ~~~~~~~~~~~~~
#
# The :func:`get_band_peak` function can be used to select peaks within specific frequency ranges,
# and can be used on individual FOOOF models.
#

###################################################################################################

# Extract any alpha band oscillations from the FOOOF model
print(get_band_peak(fm.peak_params_, alpha_band))

###################################################################################################
#
# You can optionally specify whether to return all oscillations within that band,
# or a singular result, which returns the highest power peak (if there are multiple).
#

###################################################################################################
# get_band_peak_group
# ~~~~~~~~~~~~~~~~~~~
#
# The :func:`get_band_peak_group` function can be used to select peaks within specific
# frequency ranges, from across a group of FOOOF fits.
#

###################################################################################################

# Generate some simulated power spectra and fit a FOOOFGroup to use
freqs, spectra, _ = gen_group_power_spectra(n_spectra=10,
                                            freq_range=[3, 40],
                                            aperiodic_params=param_sampler([[20, 2], [35, 1.5]]),
                                            gauss_params=param_sampler([[], [10, 0.5, 2]]))

###################################################################################################

# Fit FOOOF models across the group of simulated power spectra
fg = FOOOFGroup(peak_width_limits=[1, 8], min_peak_height=0.05, max_n_peaks=6, verbose=False)
fg.fit(freqs, spectra)

###################################################################################################

# Get all alpha oscillations from a FOOOFGroup object
alphas = get_band_peak_group(fg.get_all_data('peak_params'), alpha_band, len(fg))

###################################################################################################

# Check out some of the alpha data
print(alphas[0:5, :])

###################################################################################################
#
# Note that the design of :func:`get_band_peak_group` is such that it will retain
# information regarding which oscillation came from with model fit.
#
# To do so, it's output is organized such that each row corresponds to a specific
# model fit, such that the matrix returned is size [n_fits, 3].
#
# For this to work, at most 1 peak is extracted for each model fit within the specified band.
#
# If more than 1 peak are found within the band, the peak with the highest power is extracted.
# If no peaks are found, that row is filled with 'nan'.
#

###################################################################################################

# Check descriptive statistics of oscillation data
print('Alpha CF : ', np.nanmean(alphas[:, cf_ind]))
print('Alpha PW : ', np.nanmean(alphas[:, pw_ind]))
print('Alpha BW : ', np.nanmean(alphas[:, bw_ind]))

###################################################################################################
# A Note on Frequency Ranges
# --------------------------
#
# A benefit of using FOOOF to model power spectra is that you do not have to define
# a priori frequency ranges from which to extract oscillations.
#
# Nevertheless, it may still be useful to group extracted peaks into 'bands' of interest,
# which is why the aforementioned functions are offered.
#
# Since this frequency-range selection can be done after model fitting, we do recommend
# checking the model results, for example by checking a histogram of the center frequencies
# extracted across a group, in order to ensure the frequency ranges you choose reflect
# the characteristics of the data under studty.
#

###################################################################################################
# Analyzing the Aperiodic Component
# ---------------------------------

###################################################################################################

# Extract aperiodic exponent data from group results
exps = fg.get_all_data('aperiodic_params', 'exponent')

# Check out the aperiodic exponent results
print(exps)

###################################################################################################
# Comparing Across PSDs
# ---------------------
#
# Both of the examples above preserve information about which PSD particular features
# come from. If the PSDs come from across electrodes, channels or source reconstructed
# vertices, for example, extracting data in this way can be used to examine topographical
# relationships within and between these features.
#
# If your data comes from M/EEG, `MNE <https://github.com/mne-tools/mne-python>`_ has
# visualization tools that you can use to, with a channel file and a vector of FOOOF
# output data, visualize FOOOF results across the scalp and/or cortex.
#

###################################################################################################
# Example FOOOF-related analyses
# ------------------------------
#
# - Characterizing oscillations & aperiodic properties,
#   and analyzing spatial topographies, across demographics, modalities, and tasks
# - Comparing oscillations within and between subjects across different tasks of interest
# - Predicting disease state based on FOOOF derived oscillation & aperiodic features
# - Using FOOOF on a trial by trial manner to decode task properties, and behavioural states
#

###################################################################################################
#
# This is the end of the FOOOF tutorial materials!
#
# If you are having any troubles, please submit an issue on Github `here
# <https://github.com/fooof-tools/fooof>`_, and/or get in contact with
# us at voytekresearch@gmail.com.
#
