"""
Custom Metrics
==============

This example covers defining and using custom metrics.
"""

# Import spectral model object
from specparam import SpectralModel

# Import Metric object for defining custom metrics
from specparam.metrics.metric import Metric

# Import function to simulate power spectra
from specparam.sim import sim_power_spectrum

###################################################################################################
# Defining Custom Metrics
# -----------------------
#
# As covered in the tutorials, the specparam module has a set of predefined metrics, wherein
# `metrics` refer to measures that are computed post model fitting to evaluate properties
# of the model fit, typically as it relates to the original data.
#
# In this tutorial, we will explore how you can also define your own custom metrics.
#
# To do so, we will start by simulating an example power spectrum to use for this example.
#

###################################################################################################

# Define simulation parameters
ap_params = [50, 2]
gauss_params = [10, 0.5, 2, 20, 0.3, 4]
nlv = 0.05

# Simulate an example power spectrum
freqs, powers = sim_power_spectrum([3, 50], {'fixed' : ap_params}, {'gaussian' : gauss_params},
                                   nlv, freq_res=0.25)

###################################################################################################
# Defining Custom Measure Function
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To define a custom measure, we first need to define a function that computes our metric.
#
# By convention, a custom measure functions must have at least two input arguments, with the
# first two arguments being the original data (power spectrum) and the model (modeled spectrum).
#
# Within the function, the measure of interest should be defined, such that it returns
# the result of the metric, which should be a float.
#
# For our first example, we will define a simple error metric that computes the total
# error of the model (sum of the absolute deviations).
#

###################################################################################################

# Import any functionality needed for the metric
import numpy as np

# Define a function that computes a custom metric
def compute_total_error(power_spectrum, modeled_spectrum):
    """Compute the total (summed) error between the data and the model."""

    total_err = np.sum(np.abs(power_spectrum - modeled_spectrum))

    return total_err

###################################################################################################
# The `Metric` Class
# ~~~~~~~~~~~~~~~~~~
#
# In order to use the custom metric, more information is needed. To collect this additional
# information the :class:`~specparam.metrics.metric` object is used to define a metric.
#
# The Metric object requires the following information:
#
# - `category`: a description of what kind of metric it is
# - `measure`: a label for the specific measure that is defined
# - `description`: a description of the custom metric
# - `func`: the callable that compute the metric
#

###################################################################################################

# Define Metric for the total error
total_error_metric = Metric(
    category='error',
    measure='total_error',
    description='Total absolute error.',
    func=compute_total_error,
)

###################################################################################################
#
# Our custom metric is now defined!
#
# The use this metric, we can initialize a model object and pass in the custom metric
# to use for fitting.
#
# Note that in this example, we will use the :class:`~specparam.SpectralModel` object for our
# example, but you can also take the same approach to define custom fit modes with other
# model object (e.g. for groups of spectra or across time).
#

###################################################################################################

# Initialize a spectral model, passing in our custom metric definition
fm = SpectralModel(min_peak_height=0.25, metrics=[total_error_metric])

# Fit the model and print a report
fm.report(freqs, powers)

###################################################################################################
#
# Note that in the above report, the metrics section now includes the result of our custom metric!
#

###################################################################################################
# Defining Metrics with Dictionaries
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# In the above, we directly used the `Metric` object to define our custom metric.
#
# If you prefer, you can also collect the relevant information needed to define a metric into
# a dictionary, and pass this into the model object instead.
#

###################################################################################################

# Define the information for a custom metric, in a dictionary
custom_metric_dict = {
    'category' : 'error',
    'measure' : 'total_error',
    'description' : 'Total absolute error.',
    'func' : compute_total_error,
}

###################################################################################################

# Initialize a model object, passing in the custom metric, defined as a dictionary
fm = SpectralModel(min_peak_height=0.25, metrics=[custom_metric_dict])

###################################################################################################
#
# When using custom metrics, you can also access the results using the
# :meth:`~specparam.SpectralModel.get_metrics` by using the measure name,
# the same as when accessing default / built in metrics.
#

###################################################################################################

# Fit the model to the data
fm.fit(freqs, powers)

# Access the custom metric result with get_metrics
fm.get_metrics('total_error')

###################################################################################################
#
# Above, we initialized our model object by specifying to use only our new custom metric.
#
# Note that you can also initialize the model object with a list of multiple metrics,
# including a mixture of pre-defined and/or custom defined metrics.
#

###################################################################################################

# Initialize a spectral model, passing in multiple metrics (both internal and custom)
fm = SpectralModel(min_peak_height=0.25, metrics=[total_error_metric, 'gof_rsquared'])

# Fit the model and print a report
fm.report(freqs, powers)

###################################################################################################
#
# In the above report, we now see multiple metrics have been applied to the model, including
# our new / custom metric as well as the built-in metrics which we specified.
#

###################################################################################################
# Custom Metrics with Additional Arguments
# ----------------------------------------
#
# In some cases, you may want to define a metric that requires additional information than just
# the data and model to compute the measure of interest (e.g., the custom metric function has
# more than two arguments).
#
# For an example of this, we will define an example custom metric that computes the error
# of a specific frequency range, therefore requiring information about the frequency definition
# of the data.
#
# We start, as above, by defining a function that computes our metric, starting with the same
# two arguments (data and model) and then adding additional arguments as needed.
#

###################################################################################################

from specparam.utils.spectral import trim_spectrum

def compute_lowfreq_error(power_spectrum, modeled_spectrum, freqs):
    """Compute the mean absolute error in the low frequency range."""

    low_freq_range = [1, 8]
    _, power_spectrum_low = trim_spectrum(freqs, power_spectrum, low_freq_range)
    _, modeled_spectrum_low = trim_spectrum(freqs, modeled_spectrum, low_freq_range)

    low_err = np.abs(power_spectrum_low - modeled_spectrum_low).mean()

    return low_err

###################################################################################################
#
# In the above error function, we need  access to the frequency definition, as well as the
# data and model. Now we need to make sure that when this function is called to compute
# the metric, this additional information is made available to the function.
#
# To provide access to additional attributes, we need to use the optional `kwargs` argument
# when defining our Metric to define how to access the additional information.
#
# To use kwargs, define a dictionary where each key is the string name of the additional input
# to the measure function, and each value is a lambda function that accepts as input the model
# data & results objects, and then uses these to access the information that is needed.
#
# For our low frequency error measure, this looks like:
#
# `kwargs={'freqs' : lambda data, results: data.freqs}`
#
# Internally, if `kwargs` is defined, the lambda function is called for each entry,
# passing in the Model.data and Model.results objects, which then accesses the specified
# attributes based on the implementation of the lambda function.
#
# Note that this means all additional inputs to the function need to be information that
# can be accessed and/or computed based on what is available in the data and results
# objects that are part of the model object
#

###################################################################################################

# Define Metric for the low frequency error, defining `kwargs`
lowfreq_error = Metric(
    category='error',
    measure='low_freq_mae',
    description='Mean absolute error of the low frequency range.',
    func=compute_lowfreq_error,
    kwargs={'freqs' : lambda data, results: data.freqs},
)

###################################################################################################
#
# Now our custom metric is defined, and we can use it with a model object the same as before!
#

###################################################################################################

# Initialize a spectral model, passing in custom metric with additional arguments
fm = SpectralModel(metrics=[lowfreq_error])

# Fit the model and print a report
fm.report(freqs, powers)

###################################################################################################
#
# In the above, our new custom metric was now computed for our model fit!
#

###################################################################################################
# A Final Example
# ---------------
#
# For one last example, lets make a more complex metric, which requires multiple additional
# pieces of information that need to be accessed from the model object.
#
# In this example, we will define and use a custom metric that defines an error metric
# that is proportional to the model degrees of freedom.
#

###################################################################################################

# Define a function to compute our custom error metric
def custom_measure(power_spectrum, modeled_spectrum, freqs, n_params):
    """Compute a custom error metric of error proportional to model degrees of freedom."""

    # Compute degrees of freedom (# data points - # parameters)
    df_error = len(freqs) - n_params

    # Compute the total error of the model fit
    err_total = compute_total_error(power_spectrum, modeled_spectrum)

    # Compute the error proportional to model degrees of freedom
    err_per_df = err_total / df_error

    return err_per_df

###################################################################################################
#
# Now that we have defined the function, we define a Metric object, as before.
#
# Note that in defining the 'category' for our custom metric, we need not use the existing
# categories from the built in metrics, and can instead define our own custom category.
#

###################################################################################################

# Define Metric for the low frequency error
custom_measure = Metric(
    category='custom',
    measure='err-by-df',
    description='Error proportionate to the degrees of freedom of the model.',
    func=custom_measure,
    kwargs={'freqs' : lambda data, results: data.freqs,
            'n_params' : lambda data, results : results.n_params},
)

###################################################################################################

# Initialize a spectral model, passing in our new custom measure
fm = SpectralModel(metrics=[custom_measure])

# Fit the model and print a report
fm.report(freqs, powers)

###################################################################################################
#
# We can again use `get_metrics` to access the metric results - note that in this case
# we need to match the category name that we used in defining our metric.
#

###################################################################################################

# Access the custom metric result
fm.get_metrics('custom_err-by-df')

###################################################################################################
#
# That covers how to define custom metrics!

###################################################################################################
# Adding New Metrics to the Module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# As a final note, if you look into the set of 'built-in' metrics that are available within
# the module, you will see that these are defined in the exact way as done here - the only
# difference is that they are defined within the module and therefore can be accessed via
# their name, as a shortcut, rather than the user having to pass in their own full definitions.
#
# This also means that if you have a custom metric that you think would be of interest to
# other specparam users, once the Metric object is defined it is quite easy to add this
# to the module as a new default option. If you would be interested in suggesting a metric
# be added to the module, feel free to open an issue and/or pull request.
#
