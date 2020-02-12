"""Utilities for working with parameters."""

import numpy as np

###################################################################################################
###################################################################################################

def compute_knee_frequency(knee, exponent):
    """Compute the frequency value of the knee given the aperiodic parameter values.

    Parameters
    ----------
    knee : float
        Knee parameter value.
    exponent : float
        Exponent parameter value.

    Returns
    -------
    float
        Frequency value, in Hz, at which the knee occurs.
    """

    return np.power(knee, 1/exponent)
