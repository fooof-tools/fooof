"""
06: Further Analysis
====================
"""

###################################################################################################
#
# This tutorial explores some basic examples analyzing the results from fitting FOOOF models.
#

###################################################################################################
# Exploring FOOOF Analyses
# ------------------------
#
# FOOOF is really a way to extract features of interest from your data.
#
# These features can then be examined across or between groups of interest,
# or perhaps fed into further analysis.
#
# Largely, it is up to you what to do after running FOOOF,
# and depends on your questions of interest.
#
# Here, we briefly introduce some analysis utilities that are packaged with FOOOF,
# and explore some simple analyses that can be done with FOOOF outputs.

###################################################################################################

# General imports
import numpy as np

# Import FOOOF objects & synth utilities
from fooof import FOOOF, FOOOFGroup
from fooof.synth.params import param_sampler
from fooof.synth.gen import gen_group_power_spectra

# FOOOF comes with some basic analysis function to work with FOOOF outputs
from fooof.analysis import get_band_peak, get_band_peak_group

###################################################################################################

# Reload some data and fit a FOOOF model to use
freqs = np.load('dat/freqs_lfp.npy')
spectrum = np.load('dat/spectrum_lfp.npy')
fm = FOOOF(peak_width_limits=[2, 8])
fm.fit(freqs, spectrum, [3, 30])

###################################################################################################

# Generate some synthetic power spectra and fit a FOOOFGroup to use
freqs, spectra, _ = gen_group_power_spectra(n_spectra=10,
                                            freq_range=[3, 40],
                                            aperiodic_params=param_sampler([[20, 2], [35, 1.5]]),
                                            gauss_params=param_sampler([[], [10, 0.5, 2]]))
fg = FOOOFGroup(peak_width_limits=[1, 8], min_peak_amplitude=0.05, max_n_peaks=6, verbose=False)
fg.fit(freqs, spectra)

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
cf_ind, am_ind, bw_ind = 0, 1, 2

# Define frequency bands of interest
theta_band = [4, 8]
alpha_band = [8, 12]
beta_band = [15, 30]

###################################################################################################
# Use :func:`get_band_peak` to extract oscillations from a single FOOOF model

# Extract any beta band oscillations from the FOOOF model
get_band_peak(fm.peak_params_, beta_band)

###################################################################################################
#
# The :func:`get_band_peak` function will extract peaks within a specified band from
# the results of a FOOOF fit.
#
# You can optionally specify whether to return all oscillations within that band,
# or a singular result, which returns the highest power peak (if there are multiple).

###################################################################################################

# Get all alpha oscillations from a FOOOFGroup object
alphas = get_band_peak_group(fg.get_all_data('peak_params'), alpha_band, len(fg))

###################################################################################################

# Check out some of the alpha data
alphas[0:5, :]

###################################################################################################
# **get_band_peak_group**
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

###################################################################################################

# Check descriptive statistics of oscillation data
print('Alpha CF : ', np.nanmean(alphas[:, cf_ind]))
print('Alpha Amp: ', np.nanmean(alphas[:, am_ind]))
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

###################################################################################################
# Analyzing the Aperiodic ('background') Signal
# ---------------------------------------------

###################################################################################################

# Extract aperiodic exponent data from group results
exps = fg.get_all_data('aperiodic_params', 'exponent')

# Check out the aperiodic exponent results
exps

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

###################################################################################################
# Example FOOOF-related analyses
# ------------------------------
#
# - Characterizing oscillations & aperiodic properties,
#   and analyzing spatial topographies, across demographics, modalities, and tasks
# - Comparing oscillations within and between subjects across different tasks of interest
# - Predicting disease state based on FOOOF derived oscillation & aperiodic features
# - Using FOOOF on a trial by trial manner to decode task properties, and behavioural states

###################################################################################################
#
# This is the end of the FOOOF tutorial materials!
#
# If you are having any troubles, please submit an issue on Github `here
# <https://github.com/voytekresearch/fooof>`_, and/or get in contact with
# us at voytekresearch@gmail.com.
