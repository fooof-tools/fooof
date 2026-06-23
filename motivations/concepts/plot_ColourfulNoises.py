"""
Aperiodic Activity
==================

Exploring properties of aperiodic signals, with power across all frequencies.

This example uses the
`neurodsp <https://neurodsp-tools.github.io/>`_
module for time series simulations & analyses.
"""

###################################################################################################
# Non-Frequency Specific Power
# ----------------------------
#
# colours of noise
# synaptic noise
# knees / multi-fractals?
#

###################################################################################################

# Import numpy
import numpy as np

# ...
from neurodsp.plts import plot_time_series
from neurodsp.spectral import compute_spectrum_welch
from neurodsp.sim import sim_powerlaw, set_random_seed

###################################################################################################
# Colored Noise Signals
# ~~~~~~~~~~~~~~~~~~~~~
#
# Let's now look at 'noise' signals.
#
# In the signals below, we will simulate colored noise signals, in which samples are
# drawn randomly from noise distributions, with no rhythmic properties.
#
# As we will see, in the power spectrum, these signals exhibit power at all frequencies,
# with specific patterns of powers across frequencies, which is dependent on the 'color'
# of the noise.
#

###################################################################################################
# White Noise
# ^^^^^^^^^^^
#
# A 'white noise' signal is one that is created with uncorrelated samples drawn from
# a random distribution. Since each element of the signal is sampled randomly,
# there is no consistent rhythmic structure in the signal.
#

###################################################################################################

# Simulate a white noise time series signal
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
# with equal power across all frequencies. This is the definition of white noise.
#
# This is similar to the delta function, though note that in this case the power across
# frequencies is representing continuous aperiodic activity, rather than a single transient.
#

###################################################################################################
# Pink Noise
# ^^^^^^^^^^
#
# Other 'colors' of noise refer to different patterns of power distributions
# in the power spectrum.
#
# For example, pink noise is a signal where power systematically decreases across
# frequencies in the power spectrum.
#

###################################################################################################

# Simulate a pink noise signal
pink_sig = sim_powerlaw(n_seconds, s_rate, exponent=-1)

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
# The 'colored noise' signals above are simulated signals with no rhythmic properties,
# in the sense that there are no characteristic frequencies or visible rhythms in the data.
#
# Nevertheless, and by definition, in the power spectra of such signals, there is power across
# all frequencies, with some pattern of power across frequencies.
#
# However, there are no frequencies at which power is different from expected from an
# aperiodic noise signal. These signals are statistically, by definition, aperiodic.
#



###################################################################################################


###################################################################################################


###################################################################################################


###################################################################################################
