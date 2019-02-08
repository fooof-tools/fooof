"""
Creating Synthetic Power Spectra
================================
"""

###################################################################################################
# This example covers using FOOOF to create synthetic power spectra.
#

###################################################################################################

# Import fooof functions for creating synthetic power spectra
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
# The :func:`gen_power_spectrum` function can be used to synthesize a power
# spectrum with specified parameters.
#
# Note that all FOOOF functions that synthesize power spectra take in
# gaussian parameters, not the modified peak parameters.
#

###################################################################################################

# Settings for creating a synthetic power spectrum
freq_range = [3, 40]            # The frequency range to simulate
aperiodic_params = [1, 1]       # Parameters defining the aperiodic component
gaussian_params = [10, 0.3, 1]  # Parameters for any periodic components

###################################################################################################

# Generate a synthetic power spectrum
fs, ps = gen_power_spectrum(freq_range, aperiodic_params, gaussian_params)

###################################################################################################

# Plot the synthetic power spectrum
plot_spectrum(fs, ps, log_freqs=True, log_powers=False)

###################################################################################################
# Simulating With Different Parameters
# ------------------------------------
#
# Power spectra can be synthesized with any desired parameters for the FOOOF power spectra model.
#
# The aperiodic mode for the simulated power spectrum is inferred from the parameters provided.
# If two parameters are provided, this is interpreted as [offset, exponent] for simulating
# a power spectra with a 'fixed' aperiodic component. If three parameters are provided, as in
# the example below, this is interpreted as [offset, knee, exponent] for a 'knee' spectrum.
#
# Power spectra can also be simulated with any number of peaks. Peaks can be listed in a flat
# list with [center frequency, amplitude, bandwidth] listed for as many peaks as you would
# like to add, or as a list of lists containing the same information.
#
# The following example shows simulating a different power spectrum with some different
# parameter settings, also changing the noise level added to the spectrum, and the frequency
# resolution of the simulated spectrum.
#

###################################################################################################

# Set up new settings for creating a different synthetic power spectrum
freq_range = [1, 60]
aperiodic_params = [1, 500, 2]            # Specify three values as [offset, knee, exponent]
gaussian_params = [9, 0.4, 1, 24, 0.2, 3]  # Add peaks - can also be [[9, 0.4, 1], [24, 0.2, 3]]
nlv = 0.01                                 # The amount of noise to add to the spectrum
freq_res = 0.25                            # Specific the frequency resolution to simulate

# Generate the new synthetic power spectrum
fs, ps = gen_power_spectrum(freq_range, aperiodic_params, gaussian_params, nlv, freq_res)

###################################################################################################

# Plot the new synthetic power spectrum
plot_spectrum(fs, ps, log_powers=True)

###################################################################################################
# Simulating a Group of Power Spectra
# -----------------------------------
#
# For simulating multiple power spectra, the :func:`gen_group_power_spectrum` can be used.
#
# This function takes the same kind of parameter definitions as :func:`gen_power_spectrum`,
# and in addition takes a number specifying how many power spectra to simulate, returning
# a 2D matrix containing the desired number of spectra.
#
# For each parameter that is specified, it can be a single definition, in which case
# this value is used to generate each spectrum, a list of parameters, in which case
# each successive entry is used to generate each successive power spectrum, or
# a function or generator that can be called to return parameters for each spectrum.
#

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
#
# Note that when you simulate a group of power spectra, FOOOF returns SynParam objects that
# keep track of the simulations. This, and other utilties to manage parameters and provide
# parameter definitions for synthesizing groups of power spectra are covered in the
# `Synthetic Parameters` example.
#
