"""
06: Metrics & Model Evaluation
==============================

An overview of metrics & model evaluation to examine model fit quality.
"""

###################################################################################################

# Import the model object
from specparam import SpectralModel

# Import function to check available list of metrics
from specparam.metrics.definitions import check_metrics

# Import a utility to download and load example data
from specparam.utils.download import load_example_data

###################################################################################################
# Model Metrics
# -------------
#
# In this tutorial, we will explore model metrics.
#
# The `specparam` module uses the term `metric` to refer to a measure that reflect something
# about the spectral model (but that is not computed as part of the model fit).
#
# Generally, these metrics are used to evaluate how well the model fits the data
# and thus to assess the quality of the model fits.
#
# The module comes with various available metrics. To see the list of available metrics,
# we can use the :func:`~specparam.metrics.definitions.check_metrics` function.
#

###################################################################################################

# Check the list of available metrics
check_metrics()

###################################################################################################
#
# As we can see above, metrics are organized into categories, including 'error' and 'gof'
# (goodness of fit). Within each category there are different specific measures.
#
# Broadly, error measures compute an error measure reflecting the difference between the
# full model fit and the original data. Goodness-of-fit measures compute the correspondence
# between the model and data.
#

###################################################################################################
# Specifying Metrics
# ~~~~~~~~~~~~~~~~~~
#
# Which metrics are computed depends on how the model object is initialized. When initializing
# a model object, which metrics to use can be specified using the `metrics` argument.
# When fitting a model, these metrics will then be automatically calculated after the
# model fitting and stored in the model object.
#

##################################################################################################

# Download example data files needed for this example
freqs = load_example_data('freqs.npy', folder='data')
spectrum = load_example_data('spectrum.npy', folder='data')

###################################################################################################

# Define a set of metrics to use
metrics1 = ['error_mae', 'gof_rsquared']

# Initialize model with metric specification & fit model
fm1 = SpectralModel(metrics=metrics1)
fm1.report(freqs, spectrum)

###################################################################################################
#
# After model fitting, values of the computed metrics can be accessed with the
# :func:`~specparam.SpectralModel.results.get_metrics` method.
#

###################################################################################################

print('Error: ', fm1.get_metrics('error', 'mae'))
print('GOF: ', fm1.get_metrics('gof', 'squared'))

###################################################################################################
#
# All the metric results are stored with a Metrics sub-component of the model results, from
# which you can also directly access all the metric results.
#

###################################################################################################

# Check the full set of metric results
print(fm1.results.metrics.results)

###################################################################################################
# Default Metrics
# ~~~~~~~~~~~~~~~
#
# You might notice that when specifying the metrics above, we specified metrics that have been
# available during model fitting previously, even when we did not explicitly specify them.
#
# The two specified metrics above are actually the default metrics, which are selected
# if no explicit metrics definition is given, as we've seen in previous examples.
#

###################################################################################################
# Changing Metrics
# ~~~~~~~~~~~~~~~~
#
# We can use explicit metric specification to select different metrics to compute, as in the
# next example.
#

###################################################################################################

# Define a new set of metrics to use
metrics2 = ['error_mse', 'gof_adjrsquared']

# Initialize model with metric specification & fit model
fm2 = SpectralModel(metrics=metrics2)
fm2.report(freqs, spectrum)

###################################################################################################
# Adding Additional Metrics
# ~~~~~~~~~~~~~~~~~~~~~~~~~
#
# We are also not limited to a specific number of metrics. In the following example, we can
# specify a whole selection of different metrics.
#

###################################################################################################

# Define a new set of metrics to use
metrics3 = ['error_mae', 'error_mse', 'gof_rsquared', 'gof_adjrsquared']

# Initialize model with metric specification & fit model
fm3 = SpectralModel(metrics=metrics3)
fm3.report(freqs, spectrum)

###################################################################################################
#
# Note that when using get_metrics, you specify the category and measure names.
#
# To return all available metrics within a specific category, leave the measure specification blank.
#

###################################################################################################

print(fm3.get_metrics('error'))
print(fm3.get_metrics('error', 'mse'))

###################################################################################################
#
# As before you can also check the full set of metric results from the object results.
#

###################################################################################################

print(fm3.results.metrics.results)

###################################################################################################
# Interpreting Model Fit Quality Measures
# ---------------------------------------
#
# These scores can be used to assess how the model is performing. However interpreting these
# measures requires a bit of nuance. Model fitting is NOT optimized to minimize fit error /
# maximize r-squared at all costs. To do so typically results in fitting a large number of peaks,
# in a way that overfits noise, and only artificially reduces error / maximizes r-squared.
#
# The power spectrum model is therefore tuned to try and measure the aperiodic component
# and peaks in a parsimonious manner, and, fit the `right` model (meaning the right aperiodic
# component and the right number of peaks) rather than the model with the lowest error.
#
# Given this, while high error / low r-squared may indicate a poor model fit, very low
# error / high r-squared may also indicate a power spectrum that is overfit, in particular
# in which the peak parameters from the model may reflect overfitting by fitting too many peaks.
#
# We therefore recommend that, for a given dataset, initial explorations should involve
# checking both cases in which model fit error is particularly large, as well as when it
# is particularly low. These explorations can be used to pick settings that are suitable
# for running across a group. There are not universal settings that optimize this, and so
# it is left up to the user to choose settings appropriately to not under- or over-fit
# for a given modality / dataset / application.
#

###################################################################################################
# Defining Custom Metrics
# -----------------------
#
# In this tutorial, we have explored specifying and using metrics by selecting from measures
# that are defined and available within the module. You can also define custom metrics if
# that is useful for your use case - see an example of this in the Examples.
#
