"""
02: Fitting FOOOF Models
========================

Basic usage of the FOOOF object.
"""

###################################################################################################

# Import numpy to load example data
import numpy as np

# Import the FOOOF object
from fooof import FOOOF

###################################################################################################

# Load example data to use for this tutorial (a single example power spectrum)
freqs = np.load('dat/freqs.npy')
spectrum = np.load('dat/spectrum.npy')

###################################################################################################
# FOOOF Object
# ------------
#
# Fooof is an object oriented module.
#
# At the core of the module is the FOOOF object, which holds relevant data and settings
# as attributes, and procedures to run the FOOOF algorithm as methods.
#
# The organization is similar to sklearn:
#
# - A model object is initialized, with relevant settings
# - The model is used to fit the data
# - Results can be extracted from the object
#

###################################################################################################
# FOOOF Example
# -------------
#
# The following example demonstrates fitting a FOOOF model on a single power spectrum.
#

###################################################################################################

# Initialize FOOOF model
fm = FOOOF()

# Set the frequency range upon which to fit FOOOF
freq_range = [2, 40]

# Run FOOOF model - calculates model, plots, and prints results
fm.report(freqs, spectrum, freq_range)

###################################################################################################
# FOOOF Report
# ~~~~~~~~~~~~
#
# The above method 'report', is a convenience method that calls a series of FOOOF methods:
#
# - :func:`fit`:  fits the FOOOF model
# - :func:`print_results`: prints out the results, in string form
# - :func:`plot`: plots to data and model fit
#
# Each of these methods can each be called individually.
#

###################################################################################################

# Alternatively, just fit the model with FOOOF.fit() (without printing anything)
fm.fit(freqs, spectrum, freq_range)

# After fitting, plotting and parameter fitting can be called independently:
# fm.print_results()
# fm.plot()

###################################################################################################
# FOOOF Results
# ~~~~~~~~~~~~~
#
# When the FOOOF model is calculated, the model fit parameters are stored as object
# attributes that can be accessed after fitting.
#
# Following the sklearn convention, attributes that are fit as a result of
# the model have a trailing underscore:
#
# - aperiodic\_params_
# - peak\_params_
# - error\_
# - r2\_
#

###################################################################################################
# Access model fit parameters from FOOOF object, after fitting:
#

###################################################################################################

# Aperiodic parameters
print('Aperiodic parameters: \n', fm.aperiodic_params_, '\n')

# Peak parameters
print('Peak parameters: \n', fm.peak_params_, '\n')

# Goodness of fit measures
print('Goodness of fit:')
print(' Error - ', fm.error_)
print(' R^2   - ', fm.r_squared_)

###################################################################################################
# Notes on Interpreting Peak Parameters
# -------------------------------------
#
# Peak parameters are labelled as:
#
# - CF: center frequency of the extracted peak
# - PW: power of the peak, over and above the aperiodic background
# - BW: bandwidth of the extracted peak
#
# Note that the peak parameters that are returned are not exactly the same as the
# parameters of the Gaussians used internally to fit the peaks.
#
# Specifically:
#
# - CF is the exact same as mean parameter of the Gaussian
# - PW is the height of the model fit above the aperiodic signal fit [1],
#   which is not necessarily the same as the Gaussian height
# - BW is 2 * the standard deviation of the Gaussian [2]
#
# [1] Since the Gaussians are fit together, if any Gaussians overlap,
# than the actual height of the fit at a given point can only be assessed
# when considering all Gaussians. To be better able to interpret heights
# for single peak fits, we re-define the peak height as above, and label
# it as 'power', as the units of the input data as expected to be power.
#
# [2] Standard deviation is '1 sided', where as the returned BW is '2 sided'.
#

###################################################################################################
#
# The underlying gaussian parameters are also availabe from the FOOOF object,
# in the '_gaussian_params' attribute.
#

###################################################################################################
#
# Compare the 'peak\_params_', as compared to the underlying gaussian parameters
print('  Peak Parameters \t Gaussian Parameters')
for peak, gau in zip(fm.peak_params_, fm._gaussian_params):
    print('{:5.2f} {:5.2f} {:5.2f} \t {:5.2f} {:5.2f} {:5.2f}'.format(*peak, *gau))

####################################################################################################
# FOOOFResults object
# ~~~~~~~~~~~~~~~~~~~
#
# FOOOF also has a convenience method to return all model fit results: :func:`get_results`.
#
# It returns all the model fit parameters, including the underlying Gaussian parameters.
#
# The `get_results` methods collects and returns these results as a FOOOFResults object
# (a named tuple), to keep data organized, and allow for easier collecting.
#

###################################################################################################

# Grab each model fit result with convenience method to gather all results
ap_params, peak_params, r_squared, fit_error, gauss_params = fm.get_results()

# Get results actually returns a FOOOFResult object (a named tuple)
fres = fm.get_results()

###################################################################################################

# Print out the FOOOFResults
print(fres, '\n')

# From FOOOFResults, you can access the different results
print('Aperiodic Signal Parameters: \n', fres.aperiodic_params)

# Check the r^2 and error of the model fit
print('R-squared: \n {:5.4f}'.format(fm.r_squared_))
print('Fit error: \n {:5.4f}'.format(fm.error_))
