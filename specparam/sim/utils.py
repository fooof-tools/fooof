"""Utilities related to simulations."""

import numpy as np

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
