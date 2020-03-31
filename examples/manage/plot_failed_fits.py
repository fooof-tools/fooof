"""
Failed Model Fits
=================

Example of model fit failures and how to debug them.
"""

###################################################################################################

# Import the FOOOFGroup object
from fooof import FOOOFGroup

# Import simulation code to create test power spectra
from fooof.sim.gen import gen_group_power_spectra

# Import FitError, which we will use to help debug model fit errors
from fooof.core.errors import FitError

###################################################################################################
# Model Fit Failures
# ------------------
#
# The power spectrum model is not guaranteed to fit - sometimes the fit procedure can fail.
#
# Model fit failures are rare, and they typically only happen on spectra that are
# particular noisy, and/or are some kind of outlier for which the fitting procedure
# fails to find a good model solution.
#
# In general, model fit failures should lead to a clean exit, meaning that
# a failed model fit does not lead to a code error. The failed fit will be encoded in
# the results as a null model, and the code can continue onwards.
#
# In this example, we will look through what it looks like when model fits fail.
#

###################################################################################################

# Simulate some example power spectra to use for the example
freqs, powers = gen_group_power_spectra(25, [1, 50], [1, 1], [10, 0.25, 3],
                                        nlvs=0.1, freq_res=0.25)

###################################################################################################

# Initialize a FOOOFGroup object, with some desired settings
fg = FOOOFGroup(min_peak_height=0.1, max_n_peaks=6)

###################################################################################################

# Fit power spectra
fg.fit(freqs, powers)

###################################################################################################
#
# If there are failed fits, these are stored as null models.
#
# Let's check if there were any null models, from model failures, in the models
# that we have fit so far. To do so, the :class:`~fooof.FOOOFGroup` object has some
# attributes that provide information on any null model fits.
#
# These attributes are:
#
# - ``n_null_`` : the number of model results that are null
# - ``null_inds_`` : the indices of any null model results
#

###################################################################################################

# Check for failed model fits
print('Number of Null models  : \t', fg.n_null_)
print('Indices of Null models : \t', fg.null_inds_)

###################################################################################################
# Inducing Model Fit Failures
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# So far, we have no model failures (as is typical).
#
# For this example, to induce some model fits, we will use a trick to change the number of
# iterations the model uses to fit parameters (`_maxfev`), making it much more likely to fail.
#
# Note that in normal usage, you would likely never want to change the value of `_maxfev`,
# and this here is a 'hack' of the code in order to induce reproducible failure modes
# in simulated data.
#

###################################################################################################

# Hack the object to induce model failures
fg._maxfev = 50

###################################################################################################

# Try fitting again
fg.fit(freqs, powers)

###################################################################################################
#
# As we can see, there are now some model fit failures! Note that, as above, it will
# be printed out if there is as model fit failure when in verbose mode.
#

###################################################################################################

# Check how many model fit failures we have failed model fits
print('Number of Null models  : \t', fg.n_null_)
print('Indices of Null models : \t', fg.null_inds_)

###################################################################################################
# Debug Mode
# ----------
#
# There are multiple possible reasons why a model fit failure can occur, or at least
# multiple possible steps in the algorithm at which the fit failure can occur.
#
# If you have a small number of fit failures, you can likely just exclude them.
#
# However, if you have multiple fit failures, and/or you want to investigate why the
# model is failing, you can use the debug mode to get a bit more information about
# where the model is failing.
#
# The debug mode will stop the FOOOF object catching and continuing any model
# fit errors, allowing you to see where the error is happening, and get more
# information about where it is failing.
#
# Note that here we will run the fitting in a try / except to catch the error and
# print it out, without the error actually being raised (for website purposes).
# If you just want to see the error, you can run the fit call without the try/except.
#

###################################################################################################

# Set FOOOFGroup into debug mode
fg.set_debug_mode(True)

###################################################################################################

# Refit in debug mode, in which failed fits will raise an error
try:
    fg.fit(freqs, powers)
except FitError as fooof_error:
    print(fooof_error)

###################################################################################################
# Debugging Model Fit Errors
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# This debug mode should indicate in which step the model is failing, which might indicate
# what aspects of the data to look into, and/or which settings to try and tweak.
#
# Also, all known model fit failures should be caught by the object, and not raise an
# error (when not in debug mode). If you are finding examples in which the model is failing
# to fit, and raising an error (outside of debug mode), then this might be an unanticipated
# issue with the model fit.
#
# If you are unsure about why or how the model is failing to fit, consider
# opening an `issue <https://github.com/fooof-tools/fooof/issues>`_ on the project
# repository, and we will try to look into what seems to be happening.
#
