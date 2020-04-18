""""Simulation sub-module for FOOOF."""

# Link the Sim Params object into `sim`, so it can be imported from here
from fooof.data import SimParams

from .gen import gen_freqs, gen_power_spectrum, gen_group_power_spectra
