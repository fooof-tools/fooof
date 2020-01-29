"""
Simulated Parameters
====================

Manage parameters for creating simulated power spectra.
"""

###################################################################################################

# Import fooof functions for creating spectra and managing parameters
from fooof.sim.params import param_sampler, param_iter, param_jitter, Stepper
from fooof.sim.gen import gen_power_spectrum, gen_group_power_spectra

# Import some fooof plotting functions
from fooof.plts.spectra import plot_spectrum, plot_spectra

###################################################################################################
# SimParams
# ~~~~~~~~~
#
# When you simulate multiple power spectra, FOOOF uses `SimParams` objects to
# keep track of the parameters used for each power spectrum.
#
# SimParams objects are named tuples with the following fields:
# - `aperiodic_params`
# - `gaussian_params`
# - `nlv`
#

###################################################################################################

# Set up settings for simulating a group of power spectra
n_spectra = 2
freq_range = [3, 40]
ap_params = [[0.5, 1], [1, 1.5]]
gauss_params = [[10, 0.4, 1], [10, 0.2, 1, 22, 0.1, 3]]
nlv = 0.02

###################################################################################################

# Simulate a group of power spectra
fs, ps, sim_params = gen_group_power_spectra(n_spectra, freq_range, ap_params, gauss_params, nlv)

###################################################################################################

# Print out the SimParams objects that track the parameters used to create power spectra
for sim_param in sim_params:
    print(sim_param)

###################################################################################################

# You can also use a SimParams object to regenerate a particular power spectrum
cur_params = sim_params[0]
fs, ps = gen_power_spectrum(freq_range, *cur_params)

###################################################################################################
# Managing Parameters
# -------------------
#
# FOOOF provides some helper functions for managing and selecting parameters for
# simulating groups of power spectra, including :func:`param_sampler`
# which can be used to sample parameters from list of options, and :func:`param_iter`
# which can be used to iterate across parameters.
#

###################################################################################################
# param_sampler
# ~~~~~~~~~~~~~
#
# The :func:`param_sampler` function takes a list of parameter options and randomly selects from
# the parameters to create each power spectrum. You can optionally specify the
# probabilities with which to sample from the parameter options.
#

###################################################################################################

# Create a sampler to choose from two options for aperiodic parameters
ap_opts = param_sampler([[1, 1.25], [1, 1]])

# Create sampler to choose from two options for periodic parameters, and specify probabilities
gauss_opts = param_sampler([[10, 0.5, 1], [[10, 0.5, 1], [20, 0.25, 2]]], [0.75, 0.25])

###################################################################################################

# Generate some power spectra, using the param samplers
fs, ps, sim_params = gen_group_power_spectra(10, [3, 40], ap_opts, gauss_opts)

###################################################################################################

# Plot some of the spectra that were generated
plot_spectra(fs, ps[0:4, :], log_powers=True)

###################################################################################################
# param_iter
# ~~~~~~~~~~
#
# The :func:`param_iter` function can be used to create iterators that can 'step' across
# a range of parameter values to be simulated.
#
# The :class:`Stepper` object needs to be used in conjunction with :func:`param_iter`,
# as it specifies the values to be iterated across.
#

###################################################################################################

# Set the aperiodic parameters to be stable
ap_params = [1, 1]

# Use a stepper object to define the range of values to step across
#   Stepper is defined with `start, stop, step`.
#   Here we'll define a step across alpha center frequency values
cf_steps = Stepper(8, 12, 1)

# We can use use param_iter, with our Stepper object, to create the full peak params
#   The other parameter values will be held constant as we step across CF values
gauss_params = param_iter([cf_steps, 0.4, 1])

###################################################################################################

# Generate some power spectra, using param iter
fs, ps, sim_params = gen_group_power_spectra(len(cf_steps), [3, 40], ap_params, gauss_params)

###################################################################################################

# Plot the generated spectra
plot_spectra(fs, ps, log_freqs=True, log_powers=True)

###################################################################################################
# param_jitter
# ~~~~~~~~~~~~
#
# The :func:`param_jitter` function can be used to create iterators that can sample from
# sets of parameters, applying some jitter to them.
#

###################################################################################################

# Define default aperiodic values, with some jitter
#   The first input is the default values, the second the scale of the jitter
#   You can set zero for any value that should not be jittered
ap_params = param_jitter([1, 1], [0.0, 0.15])

# Define the peak parameters, to be stable, with an alpha and a beta
gauss_params = [10, 0.2, 1, 22, 0.1, 3]

###################################################################################################

# Generate some power spectra, using param jitter
fs, ps, sim_params = gen_group_power_spectra(5, [3, 40], ap_params, gauss_params)

###################################################################################################

# Plot the generated spectra
plot_spectra(fs, ps, log_freqs=True, log_powers=True)

###################################################################################################
#
# We can see that in the generated spectra above, there is some jitter
# to the simulated aperiodic exponent values.
#
