"""Utilities related to simulations."""

import numpy as np

from specparam.sim.gen import gen_freqs as create_freqs

###################################################################################################
###################################################################################################

def set_random_seed(seed_value=0):
    """Set the random seed value.

    Parameters
    ----------
    seed_value : int
        Seed value for the random generator.
    """

    np.random.seed(seed_value)
