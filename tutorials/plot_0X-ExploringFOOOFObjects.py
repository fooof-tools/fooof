"""
0X: Exploring the FOOOF Object
==============================
"""

###################################################################################################

# Imports
import numpy as np

from fooof import FOOOF

###################################################################################################

# Create a FOOOF object to explore
fm = FOOOF()

###################################################################################################
# Description of FOOOF methods and parameters
# -------------------------------------------
#
# FOOOF follows the following Python conventions:
#
# - all user exposed settings, data, and methods are directly accessible through the object
# - 'hidden' (internal) settings and methods have a leading underscore, indicating they are private
#
# The FOOOF object contents consist of 4 main components (groups of data / code), settings,
# data attributes, result attributes, and methods, each of which are described in more
# detail below.
#

###################################################################################################
# Settings (attributes)
# ^^^^^^^^^^^^^^^^^^^^^
#
# There are a number of parameters that control the FOOOF fitting algorithm, that
# can be set by the user when initializing the FOOOF model.
#
# There are some internal settings that are not exposed at initialization.
# These settings are unlikely to need to be accessed by the user, but can be if desired -
# they are all defined and documented in \__init\__ (there should be no other settings, or
# 'magic numbers' in any other parts of the code).
#

###################################################################################################
#
# Controlling Peak Fits
# ~~~~~~~~~~~~~~~~~~~~~
#
# **peak_width_limits (Hz)** default: [0.5, 12]
#
# Enforced limits on the minimum and maximum widths of extracted peaks, given as a list of
# [minimum bandwidth, maximum bandwidth]. We recommend bandwidths be set to be at last twice
# the frequency resolution of the power spectrum.
#
# Peak Search Stopping Criteria
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# An iterative procedures searches for candidate peaks in the flattened spectrum. Candidate
# peaks are extracted in order of decreasing amplitude, until some stopping criterion is met,
# which is controlled by the following parameters:
#
# **max_n_peaks (int)** default: infinite
#
# The maximum number of peaks that can be extracted from a given power spectrum. FOOOF will
# halt searching for new peaks when this number is reached. Note that FOOOF extracts peaks
# iteratively by amplitude (over and above the aperiodic signal), and so this approach will
# extract (up to) the _n_ largest peaks.
#
# **peak_threshold (in units of standard deviation)** default: 2.0
#
# The threshold, in terms of standard deviation of the aperiodic signal-removed power
# spectrum, above which a data point must pass to be considered a candidate peak.
# Once a candidate peak drops below this threshold, the peak search is halted (without
# including the most recent candidate).
#
# **min_peak_amplitude (units of power - same as the input spectrum)** default: 0
#
# The minimum amplitude, above the aperiodic fit, that a peak must have to be extracted
# in the initial fit stage. Once a candidate peak drops below this threshold, the peak
# search is halted (without including the most recent candidate). Note that because
# this constraint is enforced during peak search, and prior to final peak fit, returned
# peaks are not guaranteed to surpass this value in amplitude.
#
# Note: there are two different amplitude-related halting conditions for the peak searching.
# By default, the relative (standard-deviation based) threshold is defined, whereas the
# absolute threshold is set to zero (this default is because there is no general way to
# set this value without knowing the scale of the data). If both are defined, both are
# used and the peak search will halt when a candidate peak fails to pass either the absolute,
# or relative threshold.
#
# Aperiodic Signal Fitting Approach
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# **aperiodic_mode (string)** default='fixed'
#
# The fitting approach to use for the aperiodic signal.
#
# Options:
#   - 'fixed' : fits without a knee parameter (with the knee parameter 'fixed' at 0)
#   - 'knee' : fits the full exponential equation, including the 'knee' parameter
#
# Verbosity
# ~~~~~~~~~
#
# **verbose (boolean)** default='True'
#
# Whether to print out status updates and warnings.

###################################################################################################
#
# You can check all the user defined FOOOF settings with check_settings
#  The description parameter here is set to print out quick descriptions of the settings
fm.print_settings(description=True)

###################################################################################################
#
# Data (attributes)
# ^^^^^^^^^^^^^^^^^
#
# FOOOF stores the frequency vector, power spectrum, frequency range, and frequency resolution.
#
# During the fit procedure, interim (hidden) data variables are also created and used.
#

###################################################################################################

# Load a piece of example data
freqs = np.load('dat/freqs_2.npy')
spectrum = np.load('dat/spectrum_2.npy')

###################################################################################################

# Set a frequency range and add the data to the FOOOF object
freq_range = [2, 40]
fm.add_data(freqs, spectrum, freq_range)

###################################################################################################

# Check out the data attributes in the FOOOF object
print('Frequency Vector: \t', fm.freqs[0:5])
print('Frequency Range: \t', fm.freq_range)
print('Frequency Resolution: \t', fm.freq_res)
print('Power Values: \t\t', fm.power_spectrum[0:5])

###################################################################################################
#
# Methods
# ^^^^^^^
#
# Functions that operate on the FOOOF object data.
# In addition to the exposed methods, there are some internal methods called in the
# fitting procedure. These methods should not be called independently, as they may
# depend on internal state as defined from other methods.
#

###################################################################################################

# This piece of code is just a way to print out all the public methods with their description
[print(it + '\n\t' + eval('fm.' + it + '.__doc__').split('\n')[0]) \
 for it in dir(fm) if it[0] != '_' and callable(eval('fm.' + it))];

###################################################################################################
# Fitting FOOOF with Different Settings
# -------------------------------------
#
# If you wish to change these settings, then you should re-initialize
# the FOOOF object with new settings.
#
# Simply resetting the relevant attribute may not appropriately propragate the value,
# and may fail (either by erroring out, or not applying the settings properly during
# fit and returning erroneous results).
#
# Here we will re-initialize a new FOOOF object, with some new settings, and fit the model.

###################################################################################################

# Initialize FOOOF model, with some specified settings
fm = FOOOF(peak_width_limits=[1, 8], max_n_peaks=6, min_peak_amplitude=0.15)

# Fit FOOOF
fm.report(freqs, spectrum, freq_range)

###################################################################################################
#
# Results (attributes)
# ^^^^^^^^^^^^^^^^^^^^
#
# FOOOF follows the scipy convention in that any attributes that result from fitting
# to the data are indicated by a trailing underscore
#
# - fm.aperiodic\_params_, fm.peak\_params\_, fm.fooofed\_spectrum\_, fm.r\_squared\_, fm.error\_
#

print(fm.aperiodic_params_)

print(fm.peak_params_)

print(fm.r_squared_)

print(fm.error_)

print(fm.fooofed_spectrum_)

###################################################################################################
# FOOOF - Saving & Reports
# ------------------------
#
# FOOOF also has support for saving out, and loading back in, data.
#
# You have the option to specify which data to save.
#
# - results: model fit results (same as is returned in FOOOFResult)
# - settings: all public settings (everything available at initialization)
# - data: freqs & power spectrum
#
# FOOOF save creates JSON files. You can specify a file name to save or append to,
# or pass in a valid JSON file object.

###################################################################################################

# Saving FOOOF results, settings, and data
fm.save(save_results=True, save_settings=True, save_data=True)

###################################################################################################

# Loading FOOOF results
nfm = FOOOF()
nfm.load()

###################################################################################################

# Plot loaded results
#   Note: plot log to match the plot from above
nfm.plot(plt_log=True)

###################################################################################################
# Create a Report
# ---------------
#
# FOOOF also has functionality to save out a 'report' of a particular model fit.
#
# This generates and saves a PDF which contains the same output as
# 'print_results', 'plot', and 'print_settings'.

###################################################################################################

# Save out a report of the current FOOOF model fit & results
#  By default (with no inputs) this saves a PDF to current directory, with the name 'FOOOF_Report'
#    Add inputs to the method call to specify a file-name, and save-location
fm.save_report()

# Check what the generated report looks like
from IPython.display import IFrame
IFrame("FOOOF_Report.pdf", width=950, height=1200)
