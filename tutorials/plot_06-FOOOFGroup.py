"""
06: FOOOFGroup
==============

Using FOOOFGroup to run FOOOF across multiple power spectra.
"""

###################################################################################################

# FOOOF imports: import FOOOFGroup object
from fooof import FOOOFGroup

# Import some utilities for simulating some test data
from fooof.sim.params import param_sampler
from fooof.sim.gen import gen_group_power_spectra

###################################################################################################
# Simulated Power Spectra
# --------------------------
#
# FOOOF includes some support for creating simulated power-spectra, that mimic real data.
#
# Here we will use that functionality to create a matrix of power spectra to test with.
#
# Here we will use a helper function called :func:`param_sampler` that takes a
# list of possible parameters, and creates an object that randomly samples from
# them to generate power spectra.
#
# If you would like to generate single power spectra, you can use :func:`gen_power_spectrum`,
# also in `fooof.sim.gen`.
#

###################################################################################################

# Settings for simulating power spectra
n_spectra = 10
f_range = [3, 40]

# Set some options for background parameters
#  Generated spectra will have an offset of either [20, 50, 35], and exponent of [2., 2.5, 1.5]
ap_opts = param_sampler([[20, 2], [50, 2.5], [35, 1.5]])

# Set some options for peak parameters
#  Generated power spectra will have either no peaks, a 10 Hz peak, or a 10 Hz & 20 Hz peak
gauss_opts = param_sampler([[], [10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]])

###################################################################################################
#
# We can now feed these settings into :func:`gen_group_power_spectra`,
# that will generate a group of power spectra for us.
#
# Note that this function also returns a list of the parameters
# used to generate each power spectrum.
#

###################################################################################################

# Simulate the group of simulated spectra
#  Note that this function also returns a list of the parameters for each func
freqs, spectra, sim_params = gen_group_power_spectra(n_spectra, f_range, ap_opts, gauss_opts)

###################################################################################################
# FOOOFGroup
# ----------
#
# The FOOOFGroup object is very similar to the FOOOF object (programmatically, it inherits
# from the FOOOF object), and can be used in the same way.
#
# The main difference is that instead of running across a single power spectrum, it
# operates across 2D matrices containing multiple power spectra.
#
# Note that by 'group' we mean merely to refer to a group of power-spectra,
# not necessarily to a group in terms of multiple subjects or similar.
# Most likely, a FOOOFGroup will be run across a collection of spectra from across
# channels, and/or across trials, within or across subjects.
#
# The main difference with the FOOOFGroup object, is that it also contains a
# `power_spectra` attribute, which stores the matrix of power-spectra to be fit,
# and collects fit results into a `group_results` attribute.
#
# Otherwise, FOOOFGroup supports all the same functionality,
# accessed in the same way as the FOOOF object.
#
# Internally, it runs the exact same fitting procedure, per spectrum, as the FOOOF object.
#

###################################################################################################

# Initialize a FOOOFGroup object - it accepts all the same settings as FOOOF
fg = FOOOFGroup(peak_width_limits=[1, 8], min_peak_height=0.05, max_n_peaks=6)

###################################################################################################

# Fit a group of power spectra with the .fit() method
#  The key difference (compared to FOOOF) is that it takes a 2D array of spectra
#     This matrix should have the shape of [n_spectra, n_freqs]
fg.fit(freqs, spectra)

###################################################################################################

# Print out results
fg.print_results()

###################################################################################################

# Plot a summary of the results across the group
#  Note: given the simulations, we expect exponents at {1.5, 2.0. 2.5} and peaks around {10, 20}
fg.plot()

###################################################################################################
#
# Just as with the FOOOF object, you can call the convenience method `report` to run
# the fitting, and print results & plots, printing out the same as above.
#

###################################################################################################

# You can also save out PDFs reports for FOOOFGroup fits, same as with FOOOF
fg.save_report()

###################################################################################################
# FOOOFGroup Data
# ---------------
#
# FOOOFGroup collects fits across power spectra into a list of FOOOFResults objects.
#

###################################################################################################

# As it runs, FOOOFGroup collects each fit results in 'group_results'
#  `group_results` is a list of FOOOFResult objects
print(fg.group_results[0:2])

###################################################################################################
# get_all_data
# ------------
#
# To collect data across all model fits, and to select specific data results from this data
# you can use the :func:`get_all_data` method. This method lets you extract specific results
# by specifying a field, as a string, and (optionally) a specific column of that data, also
# as a string (or, optionally, as an integer index).
#

###################################################################################################

# Extract aperiodic data
aps = fg.get_all_data('aperiodic_params')
exps = fg.get_all_data('aperiodic_params', 'exponent')

# Extract peak data
peaks = fg.get_all_data('peak_params')
cfs = fg.get_all_data('peak_params', 'CF')

# Extract metadata about the model fit
errors = fg.get_all_data('error')
r2s = fg.get_all_data('r_squared')

###################################################################################################

# The full list of data you can specify is available in the documentation of :func:`get_all_data`
print(fg.get_all_data.__doc__)

###################################################################################################
#
# More information about the data you can extract is also documented in the FOOOFResults object
#

###################################################################################################

# Grab a particular FOOOFResults item
#  Note that as a shortcut, you can index the FOOOFGroup object directly to access 'group_results'
f_res = fg[0]

# Check the documentation for the FOOOFResults - with full descriptions of the resulting data.
print(f_res.__doc__)

###################################################################################################

# Check out the extracted exponent values
#  Note that this extraction will return an array of length equal to the number of model fits
#    The model fit from which each data element originated is the index of this vector
print(exps)

###################################################################################################

# Check the fit center-frequencies
#  Note when you extract peak data, an extra column is returned,
#  specifying which model fit it came from
print(cfs)

###################################################################################################
# Saving & Loading with FOOOFGroup
# --------------------------------
#
# FOOOFGroup also support saving and loading, with same options as saving from FOOOF.
#
# The only difference in saving FOOOFGroup, is that it saves out a 'jsonlines' file,
# in which each line is a JSON object, saving the specified data and results for
# a single power spectrum.
#
# Note that saving settings together with results will save out duplicated settings
# to each line in the output file, corresponding to each individual spectrum in the group,
# and so is somewhat inefficient. It is more parsimonious to save out a single settings file,
# and a separate file that includes the results.
#

###################################################################################################

# Save out FOOOFGroup settings & results (separately)
fg.save('FG_settings', save_settings=True)
fg.save('FG_results', save_results=True)

###################################################################################################

# You can then reload this group data
nfg = FOOOFGroup()
nfg.load('FG_results')

###################################################################################################

# Print results to check that the loaded group
nfg.print_results()

###################################################################################################
# Parallel Support
# ----------------
#
# FOOOFGroup also has support for running in parallel, which can speed things up as
# each power spectrum is fit independently.
#
# The fit method includes an optional parameter 'n_jobs', which if set at 1 (as default),
# will run FOOOF linearly. If you set this parameter to some other integer, fitting will
# launch 'n_jobs' number of jobs, in parallel. Setting n_jobs to -1 will launch in
# parallel across all available cores.
#
# Note, however, that running FOOOF in parallel does not gaurantee a quicker runtime overall.
# The computation time per FOOOF-fit scales with the frequency range fit over, and the
# 'complexity' of the power spectra, in terms of number of peaks. For relatively small
# numbers of power spectra (less than ~100), across relatively small frequency ranges
# (say ~3-40Hz), running in parallel may offer no appreciable speed up.
#

###################################################################################################

# Run FOOOF fit across a group of power spectra in parallel, using all cores
fg.fit(freqs, spectra, n_jobs=-1)

###################################################################################################
# Extacting Individual Fits
# -------------------------
#
# When running FOOOF across a group of power spectra, results are stored as the FOOOFResults,
# which stores (only) the results of the model fit, not the full model fits themselves.
#
# To examine individual model fits, FOOOFGroup can regenerate FOOOF objects for individual
# power spectra, with the full model available for visualization.
#

###################################################################################################

# Extract a particular spectrum, specified by index to a FOOOF object
#  Here we also specify to regenerate the the full model fit, from the results
fm = fg.get_fooof(ind=2, regenerate=True)

###################################################################################################

# Print results and plot extracted FOOOF model fit
fm.print_results()
fm.plot()
