"""
06: FOOOFGroup
==============

Using FOOOFGroup to run fit models across multiple power spectra.
"""

###################################################################################################

# Import the FOOOFGroup object
from fooof import FOOOFGroup

# Import a utility to download and load example data
from fooof.utils.download import load_fooof_data

###################################################################################################
# Fitting Multiple Spectra
# ------------------------
#
# So far, we have explored using the :class:`~fooof.FOOOF` object to fit individual power spectra.
#
# However, many potential analyses will including many power spectra that need to be fit.
#
# To support this, here we will introduce the :class:`~fooof.FOOOFGroup` object, which
# applies the model fitting procedure across multiple power spectra.
#

###################################################################################################

# Load examples data files needed for this example
freqs = load_fooof_data('group_freqs.npy', folder='data')
spectra = load_fooof_data('group_powers.npy', folder='data')

###################################################################################################
#
# For parameterizing a group of spectra, we can use a 1d array of frequency values
# corresponding to a 2d array for power spectra.
#
# This is the organization of the data we just loaded.
#

###################################################################################################

# Check the shape of the loaded data
print(freqs.shape)
print(spectra.shape)

###################################################################################################
# FOOOFGroup
# ----------
#
# The :class:`~fooof.FOOOFGroup` object is very similar to the FOOOF object (programmatically,
# it inherits from the FOOOF object), and can be used in the same way.
#
# The main difference is that instead of running across a single power spectrum, it
# operates across 2D matrices containing multiple power spectra.
#
# Note that by 'group' we mean merely to refer to a group of power-spectra. We
# are not using the term 'group' in terms of necessarily referring to multiple subjects
# or any particular idea of what a 'group' may be. A group of power spectra could
# be spectra from across channels, or across trials, or across subjects, or
# whatever organization makes sense for the analysis at hand.
#
# The main differences with the :class:`~fooof.FOOOFGroup` object, are that it uses a
# `power_spectra` attribute, which stores the matrix of power-spectra to be fit,
# and collects fit results into a `group_results` attribute.
#
# Otherwise, :class:`~fooof.FOOOFGroup` supports all the same functionality,
# accessed in the same way as the :class:`~fooof.FOOOF` object.
#
# Internally, it runs the exact same fitting procedure, per spectrum, as the FOOOF object.
#

###################################################################################################

# Initialize a FOOOFGroup object, which accepts all the same settings as FOOOF
fg = FOOOFGroup(peak_width_limits=[1, 8], min_peak_height=0.05, max_n_peaks=6)

###################################################################################################

# Fit a group of power spectra with the .fit() method
#  The key difference (compared to FOOOF) is that it takes a 2D array of spectra
#     This matrix should have the shape of [n_spectra, n_freqs]
fg.fit(freqs, spectra, [3, 30])

###################################################################################################

# Print out results
fg.print_results()

###################################################################################################

# Plot a summary of the results across the group
fg.plot()

###################################################################################################
#
# Just as with the FOOOF object, you can call the convenience method
# :meth:`fooof.FOOOFGroup.report` to run the fitting, and then print the results and plots.
#

###################################################################################################

# You can also save out PDF reports of the FOOOFGroup fits, same as with FOOOF
fg.save_report('FOOOFGroup_report')

###################################################################################################
# FOOOFGroup Results
# ------------------
#
# FOOOFGroup collects fits across power spectra, and stores them in an attribute
# called ``group_results``, which is a list of FOOOFResults objects.
#

###################################################################################################

# Check out some of the results stored in 'group_results'
print(fg.group_results[0:2])

###################################################################################################
# get_params
# ~~~~~~~~~~
#
# To collect results from across all model fits, and to select specific parameters
# you can use the :func:`~fooof.FOOOFGroup.get_params` method.
#
# This method works the same as in the :class:`~fooof.FOOOF` object, and lets you extract
# specific results by specifying a field, as a string, and (optionally) a specific column
# to extract.
#
# Since the :class:`~fooof.FOOOFGroup` object collects results from across multiple model fits,
# you should always use :func:`~fooof.FOOOFGroup.get_params` to access model parameters.
# The results attributes introduced with the FOOOF object (such as `aperiodic_params_` or
# `peak_params_`) do not store results across the group, as they are defined for individual
# model fits (and used internally as such by the FOOOFGroup object).
#

###################################################################################################

# Extract aperiodic parameters
aps = fg.get_params('aperiodic_params')
exps = fg.get_params('aperiodic_params', 'exponent')

# Extract peak parameters
peaks = fg.get_params('peak_params')
cfs = fg.get_params('peak_params', 'CF')

# Extract goodness-of-fit metrics
errors = fg.get_params('error')
r2s = fg.get_params('r_squared')

###################################################################################################

# The full list of parameters you can extract is available in the documentation of `get_params`
print(fg.get_params.__doc__)

###################################################################################################
#
# More information about the parameters you can extract is also documented in the
# FOOOFResults object.
#

###################################################################################################

# Grab a particular FOOOFResults item
#  Note that as a shortcut, you can index the FOOOFGroup object directly to access 'group_results'
f_res = fg[0]

# Check the documentation for the FOOOFResults, which has descriptions of the parameters
print(f_res.__doc__)

###################################################################################################

# Check out the extracted exponent values
#  Note that this extraction will return an array of length equal to the number of model fits
#    The model fit that each parameter relates to is the index of this array
print(exps)

###################################################################################################

# Check out some of the fit center-frequencies
#  Note when you extract peak parameters, an extra column is returned,
#  specifying which model fit it came from
print(cfs[0:10, :])

###################################################################################################
# Saving & Loading with FOOOFGroup
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# FOOOFGroup also support saving and loading, with the same options for saving out
# different things as defined and described for the FOOOF object.
#
# The only difference in saving FOOOFGroup, is that it saves out a 'jsonlines' file,
# in which each line is a JSON object, saving the specified data, settings, and results for
# a single power spectrum.
#

###################################################################################################

# Save out FOOOFGroup settings & results
fg.save('FG_results', save_settings=True, save_results=True)

###################################################################################################

# You can then reload this group
nfg = FOOOFGroup()
nfg.load('FG_results')

###################################################################################################

# Print results to check that the loaded group
nfg.print_results()

###################################################################################################
# Parallel Support
# ~~~~~~~~~~~~~~~~
#
# FOOOFGroup also has support for running in parallel, which can speed things up, since
# each power spectrum can be fit independently.
#
# The fit method includes an optional parameter ``n_jobs``, which if set at 1 (as default),
# will fit models linearly (one at a time, in order). If you set this parameter to some other
# integer, fitting will launch 'n_jobs' number of jobs, in parallel. Setting n_jobs to -1 will
# launch model fitting in parallel across all available cores.
#
# Note, however, that fitting power spectrum models in parallel does not guarantee a quicker
# runtime overall. The computation time per model fit scales with the frequency range fit over,
# and the 'complexity' of the power spectra, in terms of number of peaks. For relatively small
# numbers of power spectra (less than ~100), across relatively small frequency ranges
# (say ~3-40Hz), running in parallel may offer no appreciable speed up.
#

###################################################################################################

# Fit power spectrum models across a group of power spectra in parallel, using all cores
fg.fit(freqs, spectra, n_jobs=-1)

###################################################################################################
# Progress Bar
# ~~~~~~~~~~~~
#
# If you have a large number of spectra to fit with a :class:`~fooof.FOOOFGroup`, and you
# want to monitor it's progress, you can also use a progress bar to print out fitting progress.
#
# Progress bar options are:
#
# - ``tqdm`` : a progress bar for running in terminals
# - ``tqdm.notebook`` : a progress bar for running in Jupyter notebooks
#

###################################################################################################

# Fit power spectrum models across a group of power spectra, printing a progress bar
fg.fit(freqs, spectra, progress='tqdm')

###################################################################################################
# Extracting Individual Fits
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# When fitting power spectrum models for a group of power spectra, results are stored
# in FOOOFResults objects, which store (only) the results of the model fit,
# not the full model fits themselves.
#
# To examine individual model fits, :class:`~fooof.FOOOFGroup` can regenerate
# :class:`~fooof.FOOOF` objects for individual power spectra, with the full model available
# for visualization. To do so, you can use the :meth:`~fooof.FOOOFGroup.get_fooof` method.
#

###################################################################################################

# Extract a particular spectrum, specified by index
#  Here we also specify to regenerate the the full model fit, from the results
fm = fg.get_fooof(ind=2, regenerate=True)

###################################################################################################

# Print results and plot extracted model fit
fm.print_results()
fm.plot()

###################################################################################################
# Conclusion
# ----------
#
# Now we have explored fitting power spectrum models and running these fits across multiple
# power spectra. Next we dig deeper into how to choose and tune the algorithm settings,
# and how to troubleshoot if any of the fitting seems to go wrong.
#
