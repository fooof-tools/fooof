"""
Spectral Representations
========================

Exploring properties of time series and their corresponding frequency domain representations.

This example uses the
`neurodsp <https://neurodsp-tools.github.io/>`_
module for time series simulations & analyses.
"""

###################################################################################################
# Frequency Domain Representations
# --------------------------------
#
# Central to the motivation for parameterizing power spectra is the claim that power at a
# given frequency is not sufficient to claim that there is evidence for rhythmic, or
# periodic, activity at that frequency.
#
# This example explores and seeks to motivate this idea, by examining the relationship between
# time domain signals and their frequency domain representations, with the goal of examining
# how we can move between different representations and what this means for interpreting signals.
#

###################################################################################################
# The Fourier Theorem
# ~~~~~~~~~~~~~~~~~~~
#
# Stated informally, the Fourier theorem tells us that any time series can be represented
# as a sum of sinusoids.
#
# This is a powerful idea, as it means that we can use tools such as the Fourier transform and
# other similar measures, to compute frequency representations of *any* time series.
#
# However, just because a signal can be *represented* by sinusoids does not mean that the
# signal should be *interpreted* in terms of sine waves.
#
# Alternately stated, a frequency domain representation by itself does not mean we can or
# should conceptualize a time series as being comprised of rhythmic activity - it provides
# a possible representation of the data, not a claim for the actual components of the data.
#

###################################################################################################

# sphinx_gallery_thumbnail_number = 3

# Import numpy
import numpy as np

# Import simulation functions from neurodsp to simulate time series
from neurodsp.sim import sim_powerlaw, sim_oscillation, sim_combined, set_random_seed

# Import additional utilities from neurodsp
from neurodsp.utils import create_times
from neurodsp.spectral import compute_spectrum_welch
from neurodsp.plts import plot_time_series, plot_power_spectra

###################################################################################################

# Set random seed, for consistency creating simulated data
set_random_seed(21)

# Simulation Settings
n_seconds = 2
s_rate = 1000

# Compute an array of time values, for plotting, and check length of data
times = create_times(n_seconds, s_rate)
n_points = len(times)

###################################################################################################
# Frequency Representations of a Transient Signal
# -----------------------------------------------
#
# To examine this idea - that we can represent any signal as a power spectrum, but this does
# not mean that we should interpret them as sine waves per se - we can start with some simple
# signals with transients.
#

###################################################################################################
# The Dirac Delta
# ~~~~~~~~~~~~~~~
#
# The Dirac delta is arguably the simplest signal: a signal of all 0s,
# except for a single value of 1.
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
# Next, lets compute the frequency domain representation of the Dirac delta.
#

###################################################################################################

# Compute a power spectrum of the Dirac delta
freqs, powers = compute_spectrum_welch(dirac_sig, 100)

###################################################################################################

# Plot the power spectrum of the Dirac delta
plot_power_spectra(freqs, powers)

###################################################################################################
# Section Conclusions
# ^^^^^^^^^^^^^^^^^^^
#
# As we can see above, the power spectrum of the Dirac delta function has power
# across all frequencies!
#
# This is despite it containing a single non-zero value, and thus having no rhythmic
# properties in the time domain.
#
# The Dirac delta example serves as a proof-of-principle that observing power at a particular
# frequency does not necessarily imply that one should consider that there are any rhythmic
# properties at that frequency in the original time series.
#
# In this case, the power we see across all frequencies is a representation of transient activity
# in the time series. When there are transients (or as we will see next, aperiodic activity more
# generally) the signal can still be represented in the frequency domain as a combination of
# sine waves. However, in order to represent aperiodic activity from a basis set of periodic sine
# waves, lots of sinusoids have to be added together, giving

# signals typically look very broadband in the frequency domain.

# or aperiodic components,

#
# Notably
#


###################################################################################################
# Frequency Representations of Aperiodic Signals
# ---------------------------------------------
#
# Let's start with aperiodic signals, and examine how different types of aperiodic
# signals are represented in the frequency domain.
#

###################################################################################################

# Simulate an aperiodic signal
aperiodic_sig = sim_powerlaw(n_seconds, s_rate, exponent=-1)

###################################################################################################

# Plot the aperiodic time series
plot_time_series(times, aperiodic_sig)

###################################################################################################

# Compute the power spectrum of the aperiodic signal
freqs, powers = compute_spectrum_welch(aperiodic_sig, s_rate)

###################################################################################################

# Visualize the power spectrum of the pink noise signal
plot_power_spectra(freqs, powers)

###################################################################################################
# Frequency Representations of Periodic Signals
# ---------------------------------------------
#
# Next, lets check what frequency representations look like for time series that do have
# rhythmic activity.
#

###################################################################################################
# Sinusoidal Signals
# ~~~~~~~~~~~~~~~~~~
#
# There are many different rhythmic signals we could simulate, in terms of different
# rhythmic shapes, and or temporal properties (such as rhythmic bursts). For this
# example, we will stick to simulating continuous sinusoidal signals.
#

###################################################################################################

# Simulate an oscillating signal
osc_sig = sim_oscillation(n_seconds, s_rate, freq=10)

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
# Now let's consider the case whereby one could have a signal comprised of multiple
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

# Simulate a combined signal
combined_sig = sim_combined(n_seconds, s_rate, components)

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
# frequency does not imply any rhythmic component at that frequency. Peaks of frequency specific
# power are associated with rhythmic activity in the time series.
#
# What we have covered here are just a starting point for some properties of time
# series analysis and digital signal processing. For neural data, these properties alone
# do not tell us how to interpret neural power spectra. However, here we take them as a
# starting point that motivate why prominent rhythms in the time series can be measured
# as peaks in the power spectrum, but that absent a peak, we should not automatically
# interpret power at any given frequency as necessarily reflecting rhythmic activity.
#
