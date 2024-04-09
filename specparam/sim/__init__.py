""""Simulation sub-module."""

# Link the Sim Params object into `sim`, so it can be imported from here
from specparam.data import SimParams

from .sim import sim_power_spectrum, sim_group_power_spectra, sim_spectrogram
from .gen import gen_freqs
