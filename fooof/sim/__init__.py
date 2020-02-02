""""Simulation sub-module for FOOOF."""

# Link the Sim Params object into `sim`, so it can be imported from here
from fooof.data import SimParams

from .gen import gen_freqs, gen_power_spectrum, gen_group_power_spectra
from .params import Stepper, param_iter, param_sampler, param_jitter
from .transform import (rotate_spectrum, translate_spectrum,
                        rotate_sim_spectrum, translate_sim_spectrum)
