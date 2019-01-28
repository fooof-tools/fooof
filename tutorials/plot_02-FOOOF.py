"""
02: FOOOF
=========
"""

###############################################################################
#
# FOOOF (fitting oscillations & one over f) is a module to fit neural power spectra. This tutorial covers the fundamentals of the FOOOF codebase.
#

###############################################################################

import numpy as np

# Import the FOOOF object
from fooof import FOOOF

###############################################################################

# Load example data to use for this tutorial (a single example power spectrum)
freqs = np.load('dat/freqs.npy')
spectrum = np.load('dat/spectrum.npy')

###############################################################################
# FOOOF Object
# ------------
#
# Fooof is an object oriented module.
#
# At the core of the module is the FOOOF object, which holds relevant data and settings as attributes, and procedures to run the FOOOF algorithm as methods.
#
# The organization is similar to sklearn:
#
# - A model object is initialized, with relevant settings
# - The model is used to fit the data
# - Results can be extracted from the object

###############################################################################
# FOOOF Example
# -------------

###############################################################################

# Initialize FOOOF model
fm = FOOOF()

# Set the frequency range upon which to fit FOOOF
freq_range = [2, 40]

# Run FOOOF model - calculates model, plots, and prints results
fm.report(freqs, spectrum, freq_range)

###############################################################################
# FOOOF Report
# ~~~~~~~~~~~~
#
# The above method 'report', is a convenience method that calls a series of FOOOF methods:
#
# - :func:`fit`:  fits the FOOOF model
# - :func:`print_results`: prints out the results, in string form
# - :func:`plot`: plots to data and model fit
#
# Each of these methods ('fit', 'print_results' and 'plot') can each be called individually.

###############################################################################

# Alternatively, just fit the model with FOOOF.fit() (without any printing)
fm.fit(freqs, spectrum, freq_range)

# After fitting, plotting and parameter fitting can be called independently:
# fm.print_results()
# fm.plot()

###############################################################################
# FOOOF Results
# ~~~~~~~~~~~~~
#
# When the FOOOF model is calculated, the model fit parameters are stored as object attributes that can be accessed after fitting.
#
# Following the sklearn convention, attributes that are fit as a result of the model have a trailing underscore:
#
# - aperiodic\_params_
# - peak\_params_
# - error\_
# - r2\_

###############################################################################
# Access model fit parameters from FOOOF object, after fitting

# Aperiodic parameters
print('Aperiodic signal parameters: \n', fm.aperiodic_params_, '\n')

# Peak parameters
print('Peak parameters: \n', fm.peak_params_, '\n')

# Goodness of fit measures
print('Goodness of fit:')
print(' Error - ', fm.error_)
print(' R^2   - ', fm.r_squared_)

###############################################################################
# Notes on Interpreting Peak Parameters
# -------------------------------------
#
# Note that the peak parameters that are returned are not exactly the same as the parameters of the Gaussians used internally to fit the peaks.
#
# Specifically:
#
# - CF is the mean parameter of the Gaussian (same as the Gaussian)
# - Amp is the amplitude of the model fit above the aperiodic signal fit [1], which is not necessarily the same as the Gaussian amplitude
# - BW is 2 * the standard deviation of the Gaussian [2]
#
# [1] Since the Gaussians are fit together, if any Gaussians overlap, than the actual height of the fit at a given point can only be assessed when considering all Gaussians. To be better able to interpret amplitudes for single peak fits, we re-define the peak amplitude as above.
#
# [2] Standard deviation is '1 sided', returned BW is '2 sided'.

###############################################################################
#
# The underlying gaussian parameters are also availabe from the FOOOF object
# fm._gaussian_params

###############################################################################
#
# Compare the 'peak\_params_', as compared to the underlying gaussian parameters
print('  Peak Parameters \t Gaussian Parameters')
for peak, gau in zip(fm.peak_params_, fm._gaussian_params):
    print('{:5.2f} {:5.2f} {:5.2f} \t {:5.2f} {:5.2f} {:5.2f}'.format(*peak, *gau))

###############################################################################
#
# FOOOFResults object
# ~~~~~~~~~~~~~~~~~~~
#
# FOOOF also has a convenience method to return all model fit results: get_results().
#
# It returns all the model fit parameters, including the underlying Gaussian parameters.
#
# Get parameters actually collects and returns these results as a FOOOFResults object (a named tuple), to keep data organized, and allow for easier collecting.

###############################################################################

# Grab each model fit result with convenience method to gather all results
ap_params, peak_params, r_squared, fit_error, gauss_params = fm.get_results()

# Get results actually returns a FOOOFResult object (a named tuple)
fres = fm.get_results()

###############################################################################

# Print out the FOOOFResults
print(fres, '\n')

# From FOOOFResults, you can access the different results
print('Aperiodic Signal Parameters: \n', fres.aperiodic_params)


# Check the r^2 and error of the model fit
print('R-squared: \n {:5.4f}'.format(fm.r_squared_))
print('Fit error: \n {:5.4f}'.format(fm.error_))


###############################################################################
# Description of FOOOF methods and parameters
# -------------------------------------------
#
# FOOOF follows the following Python conventions:
#     - all user exposed settings, data, and methods are directly accessible through the object
#     - 'hidden' (internal) settings and methods ones have a leading underscore
#
# The FOOOF object contents consist of 4 main components (groups of data / code):
#
# - Settings (attributes)
#     - User exposed settings are all set in object initialization.
#         - peak_width_limits, max_n_peaks, min_peak_amplitude, peak_threshold, aperiodic_mode, verbose
#     - There are some internal settings that are not exposed at initialization. These settings are unlikely to need to be accessed by the user, but can be if desired - they are  all defined and documented in \__init\__ (there should be no other settings, or 'magic numbers' in any other parts of the code).
# - Data (attributes)
#     - FOOOF stores the frequency vector, power spectrum, frequency range, and frequency resolution.
#         - fm.freqs, fm.power_spectrum, fm.freq_range, fm.freq_res
#     - During the fit procedure, interim (hidden) data variables are also created and used
# - Results (attributes)
#     - FOOOF follows the scipy convention in that any attributes that result from fitting to the data are indicated by a trailing underscore
#         - fm.aperiodic\_params_, fm.peak\_params\_, fm.fooofed\_spectrum\_, fm.r\_squared\_, fm.error\_
# - Functions (methods)
#     - Functions that operate on the FOOOF object data.
#     - In addition to the exposed methods, there are some internal methods called in the fitting procedure. These methods should not be called independently, as they may depend on internal state as defined from other methods.


###############################################################################
#
# You can check all the user defined FOOOF settings with check_settings
#  The description parameter here is set to print out descriptions of the settings
fm.print_settings(description=True)

###############################################################################
# Fitting FOOOF with Different Settings
# -------------------------------------

###############################################################################

# Load example data - a different power spectrum
freqs = np.load('dat/freqs_2.npy')
spectrum = np.load('dat/spectrum_2.npy')

###############################################################################

# Initialize FOOOF model, with different settings
fm = FOOOF(peak_width_limits=[1, 8], max_n_peaks=6, min_peak_amplitude=0.15)

# Fit FOOOF
f_range = [2, 40]
fm.report(freqs, spectrum, f_range)

###############################################################################
# Updating Settings
# -----------------
#
# If you wish to change these settings, then you should re-initialize the FOOOF object with new settings.
#
# Simply resetting the relevant attribute may not appropriately propragate the value, and may fail (either by erroring out, or not applying the settings properly during fit and returning erroneous results).

###############################################################################
# Fitting FOOOF with Aperiodic 'Knee'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Load example data (LFP)
freqs = np.load('dat/freqs_lfp.npy')
spectrum = np.load('dat/spectrum_lfp.npy')

# Initialize FOOOF - setting to aperiodic mode to use a knee fit
fm = FOOOF(peak_width_limits=[2, 8], aperiodic_mode='knee')

# Fit FOOOF model
#  Note that this time we're specifying an optional parameter to plot in log-log
fm.report(freqs, spectrum, [2, 60], plt_log=True)

###############################################################################
# A note on interpreting the "knee" parameter
# -------------------------------------------
#
# The aperiodic fit has the form:
#
# .. math::
#    BG = 10^b * \ \frac{1}{(k + F^\chi)}
#
# The knee parameter reported above corresponds to `k` in the equation.
#
# This parameter is dependent on the frequency at which the aperiodic fit transitions from horizontal to negatively sloped.
#
# To interpret this parameter as a frequency, take the :math:`\chi`-th root of `k`, i.e.:
#
# .. math::
#    knee \ frequency = k^{1/\ \chi}

###############################################################################
# FOOOF - Saving & Reports
# ------------------------
#
# FOOOF also has report for saving out, and loading back in, data.
#
# You have the option to specify which data to save.
#
# - results: model fit results (same as is returned in FOOOFResult)
# - settings: all public settings (everything available at initialization)
# - data: freqs & power spectrum
#
# FOOOF save creates JSON files. You can specify a file name to save or append to, or pass in a valid JSON file object.

###############################################################################

# Saving FOOOF results, settings, and data
fm.save(save_results=True, save_settings=True, save_data=True)

###############################################################################

# Loading FOOOF results
nfm = FOOOF()
nfm.load()

# Plot loaded results
#   Note: plot log to match the plot from above
nfm.plot(plt_log=True)

###############################################################################
# Create a Report
# ---------------
#
# FOOOF also has functionality to save out a 'report' of a particular model fit.
#
# This generates and saves a PDF which contains the same output as 'print_results', 'plot', and 'print_settings'.

###############################################################################

# Save out a report of the current FOOOF model fit & results
#  By default (with no inputs) this saves a PDF to current directory, with the name 'FOOOF_Report'
#    Add inputs to the method call to specify a file-name, and save-location
fm.save_report()

# Check what the generated report looks like
from IPython.display import IFrame
IFrame("FOOOF_Report.pdf", width=950, height=1200)
