"""
08: Further Analysis
====================

Analyze results from fitting FOOOF models.
"""

###################################################################################################
# Exploring FOOOF Analyses
# ------------------------
#
# So far we have explored how to use FOOOF a a method to extract features
# of interest from your data - in particular measuring aperiodic and periodic activity.
#
# These features can then be examined within or between groups of interest,
# and/or fed into further analysis to examine if, for example, these features
# predict other behavioural or physiological features of interest.
# Largely, it is up to you what to do after running FOOOF, as it depends on your
# questions of interest.
#
# Here, we briefly introduce some analysis utilities that are packaged with FOOOF,
# and explore some simple analyses that can be done with FOOOF outputs.
#
# To start, we will load and fit some example data, as well as simulate a group of
# power spectra to fit with a FOOOFGroup object.
#

###################################################################################################

# General imports
import numpy as np

# Import the FOOOF and FOOOFGroup objects
from fooof import FOOOF, FOOOFGroup

# Import the Bands object, which is used to define oscillation bands
from fooof.bands import Bands

# Import FOOOF simulation code and utilities
from fooof.sim.params import param_sampler
from fooof.sim.gen import gen_group_power_spectra

# Import some of the analysis functions that come with FOOOF
from fooof.analysis import get_band_peak, get_band_peak_fm, get_band_peak_fg

###################################################################################################
# Load and Fit Example Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~
#

###################################################################################################

# Load some example data
freqs = np.load('data/freqs.npy')
spectrum = np.load('data/spectrum.npy')

###################################################################################################

# Fit a FOOOF model
fm = FOOOF(peak_width_limits=[2, 8])
fm.fit(freqs, spectrum, [3, 30])

###################################################################################################
# Simulate and Fit Group Data
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

###################################################################################################

# Generate some simulated power spectra and fit a FOOOFGroup to use
freqs, spectra = gen_group_power_spectra(n_spectra=10,
                                         freq_range=[3, 40],
                                         aperiodic_params=param_sampler([[20, 2], [35, 1.5]]),
                                         periodic_params=param_sampler([[], [10, 0.5, 2]]))

###################################################################################################

# Fit FOOOF models across the group of simulated power spectra
fg = FOOOFGroup(peak_width_limits=[1, 8], min_peak_height=0.05, max_n_peaks=6, verbose=False)
fg.fit(freqs, spectra)

###################################################################################################
# FOOOF Analysis Utilities
# ------------------------
#
# FOOOF is packaged with some analysis functions. Note that these utilities are
# generally relatively simple utilities that assist in accessing and investigating
# the model fit parameters. Analyzing FOOOF results is typically idiosyncratic to the
# goals of the project, and so we consider that this will typically require custom code,
# and seek here to offer the most general utilities, and not support all possible applications.
# Here we demonstrate some of these utility functions covering very general use cases.
#

###################################################################################################
# Analyzing Periodic Components
# -----------------------------
#
# We will start by analyzing the periodic components.
# In particular, these utilities mostly serve to help organize and extract periodic
# components, for example extracing peak that fall with oscillation band defintions.
#
# This also includes using the `Bands` object, that is provided to store band defintions.
#

###################################################################################################

# Define frequency bands of interest
bands = Bands({'theta' : [4, 8],
               'alpha' : [8, 12],
               'beta' : [15, 30]})

###################################################################################################
# get_band_peak
# ~~~~~~~~~~~~~~~~
#
# The :func:`get_band_peak` function is used to select peaks within specific frequency ranges.
#
# You can optionally specify whether to return all oscillations within that band,
# or a singular result, which returns the highest power peak (if there are multiple),
# and also apply a minimum threshold to extract peaks.
#


###################################################################################################
# get_band_peak_fm
# ~~~~~~~~~~~~~~~~
#
# You can use the :func:`get_band_peak` function directly if you have already
# extracted the peak parameters from a FOOOF object. You can also use the
# :func:`get_band_peak_fm` function and pass in a FOOOF object.
#

###################################################################################################

# Extract any alpha band oscillations from the FOOOF model
print(get_band_peak_fm(fm, bands.alpha))

###################################################################################################
# get_band_peak_fg
# ~~~~~~~~~~~~~~~~
#
# Similary, the :func:`get_band_peak_group` function can be used to select peaks within
# specific frequency ranges, from FOOOFGroup object.
#

###################################################################################################

# Get all alpha oscillations from a FOOOFGroup object
alphas = get_band_peak_fg(fg, bands.alpha)

###################################################################################################

# Check out some of the alpha data
print(alphas[0:5, :])

###################################################################################################
#
# Note that when selecting peaks from a group of model fits, we retain
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
print('Alpha CF : {:1.2f}'.format(np.nanmean(alphas[:, 0])))
print('Alpha PW : {:1.2f}'.format(np.nanmean(alphas[:, 1])))
print('Alpha BW : {:1.2f}'.format(np.nanmean(alphas[:, 2])))

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
# the characteristics of the data under study.
#

###################################################################################################
# Analyzing the Aperiodic Component
# ---------------------------------
#
# Typically for analyzing the aperiodic component of the data, aperiodic parameters
# just need to be extracted from FOOOF objects and fit into analyses of interest.
#

###################################################################################################

# Plot from the FOOOFGroup, to visualize the parameters
fg.plot()

###################################################################################################

# Extract aperiodic exponent data from group results
exps = fg.get_params('aperiodic_params', 'exponent')

# Check out the aperiodic exponent results
print(exps)

###################################################################################################
# Example FOOOF Analyses
# ----------------------
#
# Once you have extracted the parameters you can analyze them by, for example:
#
# - Characterizing oscillations & aperiodic properties,
#   and analyzing spatial topographies, across demographics, modalities, and tasks
# - Comparing oscillations within and between subjects across different tasks of interest
# - Predicting disease state based on FOOOF derived oscillation & aperiodic features
# - Using FOOOF on a trial by trial manner to decode task properties, and behavioral states
#
# So far we have only introduced the basic utilities to help with
# selecting and examing FOOOF parameters.
#
# To further explore some of these specific analyses, and explore other
# utilities that may be useful, check out the
# `examples <https://fooof-tools.github.io/fooof/auto_examples/index.html>`_
# page.
#

###################################################################################################
# Conclusion
# ----------
#
# This is the end of the main FOOOF tutorial materials!
#
# If you are having any troubles, please submit an issue on Github
# `here <https://github.com/fooof-tools/fooof>`_,
# and/or get in contact with us at voytekresearch@gmail.com.
#
