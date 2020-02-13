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

    return knee ** (1./exponent)


def compute_time_constant(knee):
    """Compute the characteristc time constant based on the knee value.

    Parameters
    ----------
    knee : float
        Knee parameter value.

    Returns
    -------
    float
        Calculated time constant value, tau, given the knee parameter.
    """

    return 1. / (2*np.pi*knee)
