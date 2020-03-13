"""
04: Exploring the FOOOF Object
==============================

Further exploring the FOOOF object, including algorithm settings and available methods.
"""

###################################################################################################

# Import numpy for loading data
import numpy as np

# Import the FOOOF object
from fooof import FOOOF

# Import utility to download example data
from fooof.utils.download import fetch_fooof_data

###################################################################################################

# Initialize a FOOOF object, to use to explore
fm = FOOOF()

###################################################################################################
# Description of FOOOF methods and parameters
# -------------------------------------------
#
# The FOOOF object contents consist of 4 main components (groups of data / code):
#
# - 1) settings attributes, that control the algorithm fitting
# - 2) data attributes, that contain and describe the data
# - 3) result attributes, that contain the results of the model fit
# - 4) methods (functions) that perform procedures for fitting models and associated utilities
#
# Each these which are described in more detail below.
#
# FOOOF follows the following Python conventions:
#
# - all user exposed settings, data, and methods are directly accessible through the object
# - 'hidden' (internal) settings and methods have a leading underscore
#
#   - you *can* access these if you need to, but one should be cautious doing so
#

###################################################################################################
# 1) Settings (attributes)
# ^^^^^^^^^^^^^^^^^^^^^^^^
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
# Controlling Peak Fits
# ~~~~~~~~~~~~~~~~~~~~~
#
# **peak_width_limits (Hz)** default: [0.5, 12]
#
# Enforced limits on the minimum and maximum widths of extracted peaks, given as a list of
# [minimum bandwidth, maximum bandwidth]. We recommend bandwidths be set to be at last twice
# the frequency resolution of the power spectrum.
#

###################################################################################################
# Peak Search Stopping Criteria
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# An iterative procedure searches for candidate peaks in the flattened spectrum. Candidate
# peaks are extracted in order of decreasing height, until some stopping criterion is met,
# which is controlled by the following parameters:
#
# **max_n_peaks (int)** default: infinite
#
# The maximum number of peaks that can be extracted from a given power spectrum. FOOOF will
# halt searching for new peaks when this number is reached. Note that FOOOF extracts peaks
# iteratively by height (over and above the aperiodic component), and so this approach will
# extract (up to) the *n* largest peaks.
#
# **peak_threshold (in units of standard deviation)** default: 2.0
#
# The threshold, in terms of standard deviation of the aperiodic-removed power
# spectrum, above which a data point must pass to be considered a candidate peak.
# Once a candidate peak drops below this threshold, the peak search is halted (without
# including the most recent candidate).
#
# **min_peak_height (units of power - same as the input spectrum)** default: 0
#
# The minimum height, above the aperiodic fit, that a peak must have to be extracted
# in the initial fit stage. Once a candidate peak drops below this threshold, the peak
# search is halted (without including the most recent candidate). Note that because
# this constraint is enforced during peak search, and prior to final peak fit, returned
# peaks are not guaranteed to surpass this value in height.
#
# Note: there are two different height-related halting conditions for the peak searching.
# By default, the relative (standard-deviation based) threshold is defined, whereas the
# absolute threshold is set to zero (this default is because there is no general way to
# set this value without knowing the scale of the data). If both are defined, both are
# used and the peak search will halt when a candidate peak fails to pass either the absolute,
# or relative threshold.
#
# Aperiodic Mode
# ~~~~~~~~~~~~~~
#
# **aperiodic_mode (string)** default='fixed'
#
# The fitting approach to use for the aperiodic component.
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
#

###################################################################################################

# You can check all the user defined FOOOF settings with check_settings
#  The description parameter here is set to print out quick descriptions of the settings
fm.print_settings(description=True)

###################################################################################################
# Changing FOOOF Settings
# ~~~~~~~~~~~~~~~~~~~~~~~
#
# Note that if you wish to change settings, then you should re-initialize
# the FOOOF object with new settings.
#
# Simply changing the value of the relevant attribute may not appropriately propagate
# the value, and thus may lead to a failure, either creating an error, or not applying
# the settings properly during fit and returning erroneous results.
#
# Here we will re-initialize a new FOOOF object, with some new settings.
#

###################################################################################################

# Re-initialize a new FOOOF model, with some specified settings
fm = FOOOF(peak_width_limits=[1, 8], max_n_peaks=6, min_peak_height=0.15)

###################################################################################################
# 2) Data (attributes)
# ^^^^^^^^^^^^^^^^^^^^
#
# FOOOF stores the following data attributes:
#
# - `freqs`: the frequency values corresponding to the data
# - `power_spectrum`: the power spectrum
# - `freq_range`: the frequency range of the data
# - `freq_res`: the frequency resolution of the data
#
# During the fit procedure, interim (hidden) data variables are also created and used.
#
# The FOOOF object also has an indicator attribute, `has_data` which indicates
# if the current object has data loaded.
#

###################################################################################################

# Download examples data files needed for this example
fetch_fooof_data('freqs_2.npy', folder='data')
fetch_fooof_data('spectrum_2.npy', folder='data')

# Load a piece of example data
freqs = np.load('data/freqs_2.npy')
spectrum = np.load('data/spectrum_2.npy')

###################################################################################################

# Set a frequency range and add the data to the FOOOF object
freq_range = [2, 40]
fm.add_data(freqs, spectrum, freq_range)

###################################################################################################

# Check if the FOOOF object has data loaded
print('Has model results: ', fm.has_data)

###################################################################################################

# Check out the data attributes in the FOOOF object
print('Frequency Range: \t', fm.freq_range)
print('Frequency Resolution: \t', fm.freq_res)
print('Frequency Values: \t', fm.freqs[0:5])
print('Power Values: \t\t', fm.power_spectrum[0:5])

###################################################################################################
#
# Now that we have picked our settings, and added the data, let's fit our FOOOF model.
#

###################################################################################################

# Fit FOOOF model to the loaded data
fm.fit()

###################################################################################################
# 3) Results (attributes)
# ^^^^^^^^^^^^^^^^^^^^^^^
#
# With our model fit, the results attributes should now hold values.
#
# Recall that FOOOF follows the scipy convention in that any attributes that contain
# model results are indicated by a trailing underscore.
#
# The model results stored by the object are:
#
# - `aperiodic\_params_`: a list of aperiodic parameters, stored as [Offset, (Knee), Exponent]
# - `peak\_params\_`: all periodic parameters, where each row is a peak, as [CF, PW, BW]
# - `r\_squared\_`: the r-squared of the model, as compared to the original data
# - `error\_`: the error of the model, as compared to the original data
#
# Other attributes which store outputs from the model are:
#
# - `fooofed\_spectrum\_`: the full model reconstruction
# - `n\_peaks\_`: a helper attribute which indicates how many peaks were fit in the model
#
# The FOOOF object also has an indicator attribute, `has_model` which indicates
# if the current object has model results available.
#

###################################################################################################

# Check if the FOOOF object has model results
print('Has model results: ', fm.has_model)

###################################################################################################

# Print out model fit results
print('aperiodic params: \t', fm.aperiodic_params_)
print('peak params: \t',fm.peak_params_)
print('r-squared: \t', fm.r_squared_)
print('fit error: \t', fm.error_)
print('fooofed spectrum: \t',fm.fooofed_spectrum_[0:5])

###################################################################################################
# 4) Methods
# ^^^^^^^^^^
#
# The FOOOF object contains a number of methods that are either used to fit
# models and access data, and/or offer extra functionality.
#
# In addition to the exposed methods, there are some internal private methods,
# with a leading underscore in their name, that are called in the
# fitting procedure. These methods should not be called directly by the user
# as they may depend on internal state of the object as defined from other methods,
# and so may not do as expected in isolation.
#

###################################################################################################

# This piece of code is just a way to print out all the public methods with their description
[print(it + '\n\t' + eval('fm.' + it + '.__doc__').split('\n')[0]) \
 for it in dir(fm) if it[0] != '_' and callable(eval('fm.' + it))];

###################################################################################################
# Saving Data & Results
# ~~~~~~~~~~~~~~~~~~~~~
#
# FOOOF also has support for saving out, and loading back in, data and results.
#
# You have the option to specify which data to save.
#
# - results: model fit results (same as is returned in FOOOFResult)
# - settings: all public settings (everything available at initialization)
# - data: freqs & power spectrum
#
# FOOOF saves data out to JSON files. You can specify a file name to save
# or append to, or pass in a JSON file object.
#

###################################################################################################

# Saving FOOOF results, settings, and data
fm.save('FOOOF_results', save_results=True, save_settings=True, save_data=True)

###################################################################################################

# Loading FOOOF results
nfm = FOOOF()
nfm.load('FOOOF_results')

###################################################################################################

# Plot loaded results
nfm.plot()

###################################################################################################
# Creating Reports
# ~~~~~~~~~~~~~~~~
#
# FOOOF also has functionality to save out a 'report' of a particular model fit.
#
# This generates and saves a PDF which contains the same output as
# 'print_results', 'plot', and 'print_settings'.
#

###################################################################################################

# Save out a report of the current FOOOF model fit & results
#  By default (with no inputs) this saves a PDF to current directory, with the name 'FOOOF_Report'
#    Add inputs to the method call to specify a file-name, and save-location
fm.save_report('FOOOF_report')

###################################################################################################

# If you're in a notebook, you can use this code to check what the generated report looks like
from IPython.display import IFrame
IFrame("FOOOF_report.pdf", width=950, height=1200)

###################################################################################################
# Conclusion
# ----------
#
# We have now fully explored the FOOOF model object, and all it contains. Next,
# we will take a deeper dive into how to choose different modes for fitting
# the aperiodic component of power spectra.
#
