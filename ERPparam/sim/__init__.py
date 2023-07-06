""""Simulation sub-module for ERPparam."""

# Link the Sim Params object into `sim`, so it can be imported from here
from ERPparam.data import SimParams

from .gen import gen_time_vector, gen_power_spectrum, gen_group_power_spectra
