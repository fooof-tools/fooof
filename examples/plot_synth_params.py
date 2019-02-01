"""
Synthetic Parameters
====================
"""

###################################################################################################
# This example covers using FOOOF to create synthetic power spectra.
#

###################################################################################################

# Import fooof functions for creating spectra and managing parameters
from fooof.synth.params import param_sampler, param_iter, Stepper
from fooof.synth.gen import gen_power_spectrum, gen_group_power_spectra

# Import some fooof plotting functions
from fooof.plts.spectra import plot_spectrum, plot_spectra

###################################################################################################
# Creating Synthetic Power Spectra
# --------------------------------
#
# FOOOF has utilities to create synthetic power spectra, whereby spectra
# are simulated with an aperiodic component with overlying peaks,
# using specified parameters.
#
# Note that all FOOOF functions that synthesize power spectra take in
# gaussian parameters, not the modified peak parameters.
#

###################################################################################################

# Settings for creating a synthetic power spectrum
freq_range = [3, 40]            # The frequency range to simulate
aperiodic_params = [1, 1]       # Parameters defining the aperiodic component
gaussian_params = [10, 0.5, 1]  # Parameters for any periodic components
nlv = 0.05                      # The amount of noise to add to the spectrum

###################################################################################################

# Generate a synthetic power spectrum
fs, ps = gen_power_spectrum(freq_range, aperiodic_params, gaussian_params, nlv)

###################################################################################################

# Plot our synthetic power spectrum
plot_spectrum(fs, ps, log_powers=True)

###################################################################################################

# Create some new settings for synthesizing a group of power spectra
n_spectra = 2
freq_range = [3, 40]
ap_params = [[0.5, 1], [1, 1.5]]
gauss_params = [10, 0.4, 1]
nlv = 0.02

###################################################################################################

# Synthesize a group of power spectra
fs, ps, syn_params = gen_group_power_spectra(n_spectra, freq_range, ap_params, gauss_params, nlv)

###################################################################################################

# Plot the power spectra that were just generated
plot_spectra(fs, ps, log_freqs=True, log_powers=True)

###################################################################################################
# SynParams
# ~~~~~~~~~
#
# When you synthesize multiple power spectra, FOOOF uses `SynParams` objects to
# keep track of the parameters used for each power spectrum.
#
# SynParams objects are named tuples with the following fields:
# - `aperiodic_params`
# - `gaussian_params`
# - `nlv`
#

###################################################################################################

# Print out the SynParams objects that track the parameters used to create power spectra
for syn_param in syn_params:
    print(syn_param)

###################################################################################################

# You can also use a SynParams object to regenerate a particular power spectrum
cur_params = syn_params[0]
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
fs, ps, syn_params = gen_group_power_spectra(10, [3, 40], ap_opts, gauss_opts)

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
# The :class:`Stepper` object needs to be used in conjuction with :func:`param_iter`,
# as it specifies the values to be iterated across.
#

###################################################################################################

# Set the aperiodic parameters to be stable
ap_params = [1, 1]

# Use a stepper object and param_iter to step across CF values for an alpha oscillation
cf_steps = Stepper(8, 12, 1)
gauss_params = param_iter([cf_steps, 0.4, 1])

###################################################################################################

# Generate some power spectra, using param iter
fs, ps, syn_params = gen_group_power_spectra(len(cf_steps), [3, 40], ap_params, gauss_params)

###################################################################################################

# Plot the generated spectra
plot_spectra(fs, ps, log_freqs=True, log_powers=True)
