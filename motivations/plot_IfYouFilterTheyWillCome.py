"""
Finding 'Oscillations' With Filters
===================================

Filtering aperiodic signals.
"""

###################################################################################################
#
# One of the corrolaries of thinking of neural signals of containing of aperiodic activity,
# with power at all frequencies is that there is always power within any arbitrarily defined
# frequency range. This power does not necessarily entail any periodic activity, but will look
# like periodic activity.
#
# In this notebook we will simulate purely aperiodic filters, and apply filters to them,
# exploring how this looks.
#

###################################################################################################

import numpy as np

# Imports from NeuroDSP to simulate time series
from neurodsp import sim, filt
from neurodsp.utils import create_times
from neurodsp.plts import plot_time_series

from fooof.bands import Bands

###################################################################################################

# Settings
s_rate = 500
n_seconds = 5
times = create_times(n_seconds, s_rate)

###################################################################################################

# Define our bands of interest
bands = Bands({
    'delta' : [1, 4],
    'theta' : [4, 8],
    'alpha' : [8, 13],
    'beta' : [13, 30],
    'low gamma' : [30, 50],
    'high gamma' : [50, 150]
})

###################################################################################################

# Create a signal
sig = sim.aperiodic.sim_synaptic_current(n_seconds, s_rate)
#sig = sim.aperiodic.sim_powerlaw(n_seconds, s_rate, exponent=-1)  # Pink Noise
#sig = sim.aperiodic.sim_powerlaw(n_seconds, s_rate, exponent=0)   # White Noise

###################################################################################################

# Plot our simulated time series
plot_time_series(times, sig)

###################################################################################################

# Check out Band-by-Band Filtering
for label, f_range in bands:
    band_sig = filt.filter_signal(sig, s_rate, 'bandpass', f_range)
    plot_time_series(times, band_sig, title=label)

###################################################################################################
# Conclusions.
# ------------
#
# Words, words, words.
#
