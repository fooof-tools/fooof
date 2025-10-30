"""
02: Fitting Power Spectrum Models
=================================

Introduction to the module, beginning with the model object.
"""

###################################################################################################

# Import the model object
from specparam import SpectralModel

# Import a utility to download and load example data
from specparam.utils.download import load_example_data

###################################################################################################

# Download example data files needed for this example
freqs = load_example_data('freqs.npy', folder='data')
spectrum = load_example_data('spectrum.npy', folder='data')

###################################################################################################
# Model Object
# ------------
#
# At the core of the module is the :class:`~specparam.SpectralModel` object, which holds relevant
# data and settings as attributes, and contains methods to run the algorithm to parameterize
# neural power spectra.
#
# The organization and use of the model object is similar to scikit-learn:
#
# - A model object is initialized, with relevant settings
# - The model is used to fit the data
# - Results can be extracted from the object
#

###################################################################################################
# Calculating Power Spectra
# ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The :class:`~specparam.SpectralModel` object fits models to power spectra.
# The module itself does not compute power spectra. Computing power spectra needs
# to be done prior to using the specparam module.
#
# The model is broadly agnostic to exactly how power spectra are computed. Common
# methods, such as Welch's method, can be used to compute the spectrum.
#
# If you need a module in Python that has functionality for computing power spectra, try
# `NeuroDSP <https://neurodsp-tools.github.io/neurodsp/>`_.
#
# Note that model objects require frequency and power values passed in as inputs to
# be in linear spacing. Passing in non-linear spaced data (such logged values) may
# produce erroneous results.
#

###################################################################################################
# Fitting an Example Power Spectrum
# ---------------------------------
#
# The following example demonstrates fitting a power spectrum model to a single power spectrum.
#

###################################################################################################

# Initialize a model object
fm = SpectralModel()

# Set the frequency range to fit the model
freq_range = [2, 40]

# Report: fit the model, print the resulting parameters, and plot the reconstruction
fm.report(freqs, spectrum, freq_range)

###################################################################################################
# Fitting Models with 'Report'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The above method 'report', is a convenience method that calls a series of methods:
#
# - :meth:`~specparam.SpectralModel.fit`: fits the power spectrum model
# - :meth:`~specparam.SpectralModel.print_results`: prints out the results
# - :meth:`~specparam.SpectralModel.plot`: plots the data and model fit
#
# Each of these methods can also be called individually.
#

###################################################################################################

# Alternatively, just fit the model with SpectralModel.fit() (without printing anything)
fm.fit(freqs, spectrum, freq_range)

# After fitting, plotting and parameter fitting can be called independently:
# fm.print_results()
# fm.plot()

###################################################################################################
# Model Parameters
# ~~~~~~~~~~~~~~~~
#
# Once the power spectrum model has been calculated, the model fit parameters are stored
# as object attributes that can be accessed after fitting.
#
# Access model fit parameters from specparam object, after fitting:
#

###################################################################################################

# Aperiodic parameters
print('Aperiodic parameters: \n', fm.results.params.aperiodic.params, '\n')

# Peak parameters
print('Peak parameters: \n', fm.results.params.periodic.params, '\n')

# Check how many peaks were fit
print('Number of fit peaks: \n', fm.results.n_peaks)

###################################################################################################
# Selecting Parameters
# ~~~~~~~~~~~~~~~~~~~~
#
# You can also select parameters using the :meth:`~specparam.SpectralModel.get_params`
# method, which can be used to specify which parameters you want to extract.
#

###################################################################################################

# Extract parameters, indicating sub-selections of parameters
exp = fm.get_params('aperiodic', 'exponent')
cfs = fm.get_params('periodic', 'CF')

###################################################################################################
#
# For a full description of how you can access data with
# :meth:`~specparam.SpectralModel.get_params`, check the method's documentation.
#
# As a reminder, you can access the documentation for a function using '?' in a
# Jupyter notebook (ex: `fm.get_params?`), or more generally with the `help` function
# in general Python (ex: `help(fm.get_params)`).
#

###################################################################################################
# Model Metrics
# ~~~~~~~~~~~~~
#
# In addition to model fit parameters, the fitting procedure computes and stores various
# metrics that can be used to evaluate model fit quality.
#

###################################################################################################

# Goodness of fit metrics
print('Goodness of fit:')
print(' Error - ', fm.results.metrics.results['error_mae'])
print(' R^2   - ', fm.results.metrics.results['gof_rsquared'], '\n')

###################################################################################################
#
# You can also access metrics with the :meth:`~specparam.SpectralModel.results.get_metrics` method.
#

###################################################################################################

# Extract a model metric with `get_metrics`
err = fm.get_metrics('error')

###################################################################################################
#
# Extracting model fit parameters and model metrics can also be combined to evaluate
# model properties, for example using the following template:
#

###################################################################################################

# Print out a custom parameter report
template = ("With an error level of {error:1.2f}, an exponent "
            "of {exponent:1.2f} and peaks of {cfs:s} Hz were fit.")
print(template.format(error=err, exponent=exp,
                      cfs=' & '.join(map(str, [round(cf, 2) for cf in cfs]))))

###################################################################################################

# Compare the 'peak_params_' to the underlying gaussian parameters
print('  Peak Parameters \t Gaussian Parameters')
for peak, gauss in zip(fm.results.params.periodic.get_params('converted'),
                       fm.results.params.periodic.get_params('fit')):
    print('{:5.2f} {:5.2f} {:5.2f} \t {:5.2f} {:5.2f} {:5.2f}'.format(*peak, *gauss))

####################################################################################################
# FitResults
# ~~~~~~~~~~
#
# There is also a convenience method to return all model fit results:
# :func:`~specparam.SpectralModel.results.get_results`.
#
# This method returns all the model fit parameters, including the underlying Gaussian
# parameters, collected together into a FitResults object.
#
# The FitResults object, which in Python terms is a named tuple, is a standard data
# object used to organize and collect parameter data.
#

###################################################################################################

# Grab each model fit result with `get_results` to gather all results together
#   Note that this returns a FitResults object
fres = fm.results.get_results()

# You can also unpack all fit parameters when using `get_results`
ap_fit, ap_conv, peak_fit, peak_conv, metrics = fm.results.get_results()

###################################################################################################

# Print out the FitResults
print(fres, '\n')

# from specparamResults, you can access the different results
print('Aperiodic Parameters: \n', fres.aperiodic_fit)

# Check the R^2 and error of the model fit
print('R-squared: \n {:5.4f}'.format(fres.metrics['gof_rsquared']))
print('Fit error: \n {:5.4f}'.format(fres.metrics['error_mae']))

###################################################################################################
# Conclusion
# ----------
#
# In this tutorial, we have explored the basics of the :class:`~specparam.SpectralModel` object,
# fitting power spectrum models, and extracting parameters.
#
# In the next tutorial, we will explore how this algorithm actually works to fit the model.
#
