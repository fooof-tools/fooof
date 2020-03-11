"""
Rhythmicity of Time Series
==========================

Exploring the rhythmicity of time series and their frequency representations.
"""

###################################################################################################
# Rhythmicity of Time Series
# --------------------------
#
# Central to the motivation for parameterizing neural power is the claim that power at a
# given frequency is not sufficient to claim that there is evidence for rhythmic activity
# at that frequency.
#
# This idea forms the basis for considering that without a peak in the power spectrum, as
# evidence for frequency specify power, observing power at a particular frequency does
# not necessarily entail that it is rhythmic.
#
# In the example, we explore some signals in the time domain, and their frequency domain
# representations, in order to investigate if and signals should be interpreted as
# being comprised of or containing periodic activity.
#

###################################################################################################
# The Fourier Theorem
# ~~~~~~~~~~~~~~~~~~~
#
# The Fourier theorem states, informally, that any time series can be represented
# as a sum of sinusoids.
#
# This is a very powerful, and useful theorem, as it means that tools such as the Fourier
# transform, and broadly equivalent measures such as wavelets, can be used to compute
# a frequency based representation of any time series data.
#
# However, just because a signal _can_ be represented by sinusoids does not mean that any
# given signal, or any given aspect of a signal, for which a power spectrum can be computed
# should be conceptualized as being comprised of rhythmic components.
#
# The power spectrum is just a possible representation of the original data, but not a
# descriptive claim of the actual components of the data.
#

###################################################################################################

import numpy as np
import matplotlib.pyplot as plt

# Use NeuroDSP for time series simulations & analyses
from neurodsp import sim
from neurodsp.utils import create_times
from neurodsp.spectral import compute_spectrum_welch
from neurodsp.plts import plot_time_series, plot_power_spectra

###################################################################################################

# Simulation Settings
n_seconds = 2
s_rate = 1000

# Compute a timepoint vector, for plotting
n_points = s_rate*n_seconds
times = create_times(n_points/s_rate, s_rate)

###################################################################################################
# Frequency Representations of Non-Rhythmic Signals
# -------------------------------------------------
#
# First, we let's explore how different types of signals, specifically non-rhythmic time
# series, are represented in frequency space.
#

###################################################################################################
# The Dirac Delta
# ~~~~~~~~~~~~~~~
#
# Let's start with the arguably the simplest signal - a signal of all zeros, except for
# a single value of 1. This signal is called the dirac delta.
#

###################################################################################################

# Simulate a delta function
dirac_sig = np.zeros([n_points])
dirac_sig[500] = 1

###################################################################################################

# Plot the time series of the delta signal
plot_time_series(times, dirac_sig)

###################################################################################################
#
# Next, lets compute the frequency representation of the delta function.
#

###################################################################################################

# Compute a power spectrum of the dirac delta
freqs, powers = compute_spectrum_welch(dirac_sig, 100)

###################################################################################################

# Plot the power spectrum of the dirac delta
plot_power_spectra(freqs, powers)

###################################################################################################
# Section Conclusions
# ^^^^^^^^^^^^^^^^^^^
#
# The power spectrum of the Dirac delta function has power across all frequencies.
#
# This is despite it containing containing a single non-zero value, and thus having
# no rhythmic properties to it in the time domain.
#
# The Dirac delta example can be taken as a proof of principle that observing power
# at a particular frequency does not necessarily imply that one should consider that
# there are any rhythmic properties at that frequency in the original time series.
#
# In this case, and many like it, power across all frequencies is a representation of
# transiest (or aperiodic) activity in the time series.
#

###################################################################################################
# Coloured Noise Signals
# ~~~~~~~~~~~~~~~~~~~~~~
#
# Let's now look at 'noise' signals.
#
# In the signals below, we will simulate coloured noise signals with, whereby samples are
# drawn randomly from noise distributions, with no rhythmic properties.
#
# As we will see, in the power spectrum, these signals exhibit power at all frequencies,
# with specific patterns of powers across frequencies, which is dependent on the 'colour'
# of the noise.
#

###################################################################################################
# White Noise
# ^^^^^^^^^^^
#
# A 'white noise' signal is generated with uncorrelated samples. Since each element
# of the signal is sampled randomly, there is no consistent rhythmic structure in the signal.
#

###################################################################################################

# Generate a white noise time series signal
white_sig = np.random.normal(0, 1, n_points)

###################################################################################################

# Plot the white noise time series
plot_time_series(times, white_sig)

###################################################################################################
#
# As before, we can compute and visualize the power spectrum of this signal.
#

###################################################################################################

# Compute the power spectrum of the white noise signal
freqs, powers = compute_spectrum_welch(white_sig, s_rate)

###################################################################################################

# Visualize the power spectrum of the white noise signal
plot_power_spectra(freqs, powers)

###################################################################################################
#
# In the frequency representation, we can see that white noise has a flat power spectrum,
# with equal power across all frequencies.
#
# This is similar to the delta function, though note that in this case the power across
# frequencies is representing continuous aperiodic activity, rather than a single transient.
#

###################################################################################################
# Pink Noise
# ^^^^^^^^^^
#
# Other 'colors' of noise refer to different patterns across frequencies in the power spectrum.
#
# For example, pink noise is a signal with a trend whereby the amount of power decreases
# systematically across increasing frequencies.
#

###################################################################################################

# Generate a pink noise signal
pink_sig = sim.sim_powerlaw(n_seconds, s_rate, exponent=-1)

###################################################################################################

# Plot the pink noise time series
plot_time_series(times, pink_sig)

###################################################################################################

# Compute the power spectrum of the pink noise signal
freqs, powers = compute_spectrum_welch(pink_sig, s_rate)

###################################################################################################

# Visualize the power spectrum of the pink noise signal
plot_power_spectra(freqs, powers)

###################################################################################################
# Section Conclusion
# ^^^^^^^^^^^^^^^^^^
#
# The 'coloured noise' signals above are simulated signals with no rhythmic properties,
# in the sense that there are no characteristic frequencies or visible rhythms in the data.
#
# Nevertheless, and by definition, in the power spectra of such signals, there is power across
# all frequencies, with some pattern across frequencies.
#
# However, there are no frequencies at which power is different from expected from an
# aperiodic noise signal.
#

###################################################################################################
# Frequency Representations of Rhythmic Signals
# ---------------------------------------------
#
# Next, lets check what frequency representations look like for time series that do have
# rhythmic activity.
#

###################################################################################################
# Sinuisoidal Signals
# ~~~~~~~~~~~~~~~~~~~
#
# There are many different rhythmic signals we could simulate, in terms of
#

###################################################################################################

# Generate an oscillating signal
osc_sig = sim.sim_oscillation(n_seconds, s_rate, freq=10)

###################################################################################################

# Plot the oscillating time series
plot_time_series(times, osc_sig)

###################################################################################################

# Compute the power spectrum of the oscillating signal
freqs, powers = compute_spectrum_welch(osc_sig, s_rate)

###################################################################################################

# Visualize the power spectrum of the oscillating signal
plot_power_spectra(freqs, powers)

###################################################################################################
# Section Conclusion
# ^^^^^^^^^^^^^^^^^^
#
# When there is rhythmic activity at a particular frequency, this exhibits as a 'peak'
# of power in the frequency domain. This peak indicates high power at a specific frequency,
# where as the power values at all other frequencies are effectively zero.
#

###################################################################################################
# Frequency Representations of Complex Signals
# --------------------------------------------
#
# Finally, let's consider the case whereby one could have a signal comprised of multiple
# components, for example one or more oscillations combined with an aperiodic component.
#

###################################################################################################
# Combined Aperiodic & Periodic Signals
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To examine this, we will simulate combined signals, comprising both periodic and aperiodic
# components, and see what the frequency representations look like.
#

###################################################################################################

# Define component of a combined signal: an oscillation and an aperiodic component
components = {
    'sim_oscillation' : {'freq' : 10},
    'sim_powerlaw' : {'exponent' : -1}
}

# Generate a combined signal
combined_sig = sim.sim_combined(n_seconds, s_rate, components)

###################################################################################################

# Plot the combined time series
plot_time_series(times, combined_sig)

###################################################################################################

# Compute the power spectrum of the combined signal
freqs, powers = compute_spectrum_welch(combined_sig, s_rate)

###################################################################################################

# Visualize the power spectrum of the combined signal
plot_power_spectra(freqs, powers)

###################################################################################################
# Section Conclusion
# ^^^^^^^^^^^^^^^^^^
#
# In the power spectrum above, we can see that combined signals, with aperiodic & periodic
# activity reflect elements of both components. The periodic power can be seen as a
# peak of power over and above the rest of the spectrum, at the frequency of the simulated
# rhythm. Across all frequencies, we also see the power contributed by the aperiodic component.
#

###################################################################################################
# Conclusion
# ----------
#
# In this example, we have seen that, in the frequency domain:
#
# - transients and aperiodic activity exhibit power across all frequencies
# - oscillations exhibit specific power, or a 'peak', at the frequency of the rhythm
# - combined signals display a combination of these properties, with power
#   across all frequencies, and overlying 'peaks' at frequencies with periodic activity
#
# Collectively, we have seen cases that motivate that simply having power at a particularly
# frequency does not imply any rhythmic component at that frequency. Peaks of frequency specfic
# power are associated with rhythmic activity in the time series.
#
# For neural data, these properties alone do not tell us how to interpret neural
# power spectra, but they can be taken as a starting point that motivate why prominent
# rhythms in the time series can be measured as peaks in the power spectrum, but that
# absent a peak, we should not automatically interpret power at any given frequency
# as necessarily reflecting rhythmic activity.
#

###################################################################################################
#
# Sphinx settings:
# sphinx_gallery_thumbnail_number = 3
#
