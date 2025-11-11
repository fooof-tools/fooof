"""
Custom Algorithms
=================

This example covers defining and using custom fit algorithms.
"""

from specparam import SpectralModel

# Import function to simulate a power spectrum
from specparam.sim import sim_power_spectrum

# Import elements to define custom fit algorithms
from specparam.algorithms.settings import SettingsDefinition
from specparam.algorithms.algorithm import Algorithm

###################################################################################################
# Defining Custom Fit Algorithms
# ------------------------------
#
# The specparam module includes a standard fitting algorithm that is used to for fitting the
# selected fit modes to the data. However, you do not have to use this particular algorithm,
# you can tweak how it works, and/or define your own custom algorithm and plug this in to
# the model object.
#
# In this tutorial, we will explore how you can also define your own custom fit algorithms.
#
# To do so, we will start by simulating an example power spectrum to use for this example.
#

###################################################################################################

# Define simulation parameters
ap_params = [0, 1]
gauss_params = [10, 0.5, 2]
nlv = 0.025

# Simulate an example power spectrum
freqs, powers = sim_power_spectrum(\
    [3, 50], {'fixed' : ap_params}, {'gaussian' : gauss_params}, nlv)

###################################################################################################
# Example: Custom Algorithm Object
# --------------------------------
#
# In our first example, we will introduce how to create a custom fit algorithm.
#
# For simplicity, we will start with a 'dummy' algorithm - one that functions code wise, but
# doesn't actually implement a detailed fitting algorithm, so that we can start with the
# organization of the code, and build up from there.
#

###################################################################################################
# Algorithm Settings
# ~~~~~~~~~~~~~~~~~~
#
# A fitting algorithm typically has some settings that you want to define and describe so that
# the user can check their description and provide values for the settings.
#
# For fitting algorithms, these setting descriptions are managed by the
# :class:`~specparam.algorithms.settings.SettingsDefinition` object.
#
# For our dummy algorithm, we will initialize a settings definition object, with a
# placeholder label and description.
#

###################################################################################################

# Create a settings definition for our dummy algorithm
DUMMY_ALGO_SETTINGS = SettingsDefinition({'fit_setting' : 'Setting description'})

###################################################################################################
# Algorithm Object
# ~~~~~~~~~~~~~~~~
#
# Now we can define our custom fitting algorithm. To do so, we will create a custom object
# that inherits from the specparam :class:`~specparam.algorithms.algorithm.Algorithm` object.
#
# Implementing a custom fit object requires following several standards for specparam
# to be able to use it:
#
# - the class should inherit from the specparam Algorithm object
# - the object needs to accept `modes`, `data`, `results`, and `debug` input arguments
# - at initialization, the object should initialize the Algorithm object ('super()'),
#   including providing a name and description, passing in the algorithm settings
#   object (from above), and passing in the 'modes', 'data', 'results', and 'debug' inputs
# - the object needs to define a `_fit` function that serves as the main fit function
#
# In the following code, we initialize a custom object following the above to create a fit
# algorithm object. Note that as a dummy algorithm, the 'fit' aspect doesn't actually
# implement a step-by-step fitting procedure, but simply instantiates a pre-specified
# model (to mimic the outputs of a fit algorithm).
#

###################################################################################################

import numpy as np

class DummyAlgorithm(Algorithm):
    """Dummy object to mimic a fit algorithm."""

    def __init__(self, modes=None, data=None, results=None, debug=False):
        """Initialize DummyAlgorithm instance."""

        # Initialize base algorithm object with algorithm metadata
        super().__init__(
            name='dummy_fit_algo',
            description='Dummy fit algorithm.',
            public_settings=DUMMY_ALGO_SETTINGS,
            modes=modes, data=data, results=results, debug=debug)

    def _fit(self):
        """Define the full fitting algorithm."""

        self.results.params.aperiodic.add_params('fit', np.array([0, 1]))
        self.results.params.periodic.add_params('fit', np.array([10, 0.5, 2], ndmin=2))
        self.results._regenerate_model(self.data.freqs)

###################################################################################################
# Expected outcomes of algorithm fitting
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# In order for a custom fitting algorithm to work properly when embedded within a model object,
# there are some expectations for what the fitting process should do.
#
# The following elements are expected to computed through the fitting procedure:
#
# - Parameter results should be added for each parameter
#     - `model.results.params.{component}.add_params(...)`
#
# - The model should be computed and added to the object
#     - `model.results.model.modeled_spectrum` should be populated, as well as model
#       components (`model.results.model._ap_fit` & `model.results.model._peak_fit`)
#
# If the above  you do the above, the model object can be used as normal, and you can do
# (fit / print_results / plot / report / as well as save and load results).
#
# There are also some additional procedures / outputs that a custom fit process may do:
#
# - Update fit parameters to also have converted versions
#

###################################################################################################

# Initialize a model object, passing in our custom dummy algorithm
fm = SpectralModel(algorithm=DummyAlgorithm)

###################################################################################################

# Fit and report model, using our custom algorithm
fm.report(freqs, powers)

###################################################################################################
#
# In this case, with our dummy algorithm, we cheated a bit - the model was pre-specified to
# initialize a model that happened to match the simulated data, and no real fitting took place.
#
# The point of this example is to show the outline of how a custom fit algorithm can be developed,
# since the `_fit` method can implement any arbitrarily defined procedure to fit a model,
#

###################################################################################################
# Example with Custom Fitting
# ---------------------------
#
# Having sketched out the basic outline with the dummy algorithm above, lets now define a custom
# fit algorithm that actually does some fitting.
#
# For simplicity, this algorithm will be a simple fit that starts with an aperiodic fit, and
# then fits a single peak to the flattened (aperiodic removed) spectrum. To do so, it will
# take in an algorithm setting that defines a guess center-frequency for this peak.
#

###################################################################################################

# Define the algorithm settings for our custom fit
CUSTOM_ALGO_SETTINGS = SettingsDefinition(\
    {'guess_cf' : 'Initial guess center frequency for peak.'})

###################################################################################################
#
# Now we need to define our fit approach! To do so, we will mimic the approach we used above
# to define a custom algorithm object, this time making the `_fit` method implement an actual
# fitting procedure. Note that while the `_fit` function should be the main method that runs
# the fitting process, it can also call additional methods. In this implementation, we define
# additional fit methods to fit each component.
#
# To fit the data components, we will use the `curve_fit` function from scipy.
#

###################################################################################################

from scipy.optimize import curve_fit

class CustomAlgorithm(Algorithm):
    """Custom fitting algorithm."""

    def __init__(self, guess_cf, modes=None, data=None, results=None, debug=False):
        """Initialize DummyAlgorithm instance."""

        # Initialize base algorithm object with algorithm metadata
        super().__init__(
            name='custom_fit_algo',
            description='Example custom algorithm.',
            public_settings=CUSTOM_ALGO_SETTINGS,
            modes=modes, data=data, results=results, debug=debug)

        ## Public settings
        self.settings.guess_cf = guess_cf

    def _fit(self):
        """Define the full fitting algorithm."""

        # Fit each individual component
        self._fit_aperiodic()
        self._fit_peak()

        # Create full model from the individual components
        self.results.model.modeled_spectrum = \
            self.results.model._peak_fit + self.results.model._ap_fit

    def _fit_aperiodic(self):
        """Fit aperiodic - direct fit to full spectrum."""

        # Fit aperiodic component directly to data & collect parameter results
        ap_params, _ = curve_fit(\
            self.modes.aperiodic.func, self.data.freqs, self.data.power_spectrum,
            p0=np.array([0] * self.modes.aperiodic.n_params))
        self.results.params.aperiodic.add_params('fit', ap_params)

        # Construct & collect aperiodic component
        self.results.model._ap_fit = self.modes.aperiodic.func(freqs, *ap_params)

    def _fit_peak(self):
        """Fit peak - single peak, with initial guess CF, to flattened spectrum."""

        # Fit peak
        self.results.model._spectrum_flat = self.data.power_spectrum - self.results.model._ap_fit
        pe_params, _ = curve_fit(\
            self.modes.periodic.func, self.data.freqs, self.results.model._spectrum_flat,
            p0=np.array([self.settings.guess_cf] + [1] * (self.modes.periodic.n_params - 1)))
        self.results.params.periodic.add_params('fit', np.atleast_2d(pe_params))

        # Construct periodic component
        self.results.model._peak_fit = self.modes.periodic.func(freqs, *pe_params)

###################################################################################################

# Initialize a model object, passing in a custom fit algorithm and settings for this algorithm
fm = SpectralModel(algorithm=CustomAlgorithm, guess_cf=10)

###################################################################################################

# Fit model with custom algorithm and report results
fm.report(freqs, powers)

###################################################################################################
#
# In the above we fit a model with our custom fit algorithm, and can see the results.
#

###################################################################################################
# Notes on Defining Custom Algorithms
# -----------------------------------
#
# In these examples, we have made quite simple algorithms. This may be a desired use case -
# creating bespoke fit approaches for specific kinds of data.
#
# In cases where generalizability is more desired, the fit algorithm is likely going to need to
# be significantly more detailed to address
#
# To see, for example, the details of the original / default fit algorithm, check the
# definition of the `spectral_fit` algorithm in the codebase, which is also defined in the same
# way as here.
#
# Additional notes to consider when creating custom algorithms:
#
# - In the above, we didn't consider different fit modes, and used the defaults. Depending on
#   your use case, the fit algorithm may or not want to make assumptions about the fit modes.
#   To make it generalize, the algorithm needs to be written in a way that is flexible for
#   applying different fit functions that may have different numbers of parameters
# - As well as the public settings we defined here, you may want to additional specify
#   a set of private settings (additional settings that are defined for the algorithm, which
#   are not expected to be changed in most use cases, but which can be accessed)
#

###################################################################################################
# Algorithms that use curve_fit
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# A common approach for fitting functions to data is to use the scipy `curve_fit`
# function to estimate parameters to fit a specified function to some data, as we did in
# an above example.
#
# When doing so, you may also want to manage and allow inputs for settings that to the
# curve_fit function to manage the fitting process. As a shortcut for this case, you can use the
# :class:`~specparam.algorithms.algorithm.AlgorithmCF` object which pre-initializes a set
# of curve_fit settings.
#
# In addition, when using `curve_fit` you are likely going to want to
#
