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
        Frequency value, in Hz, of the knee occurs.
    """

    return knee ** (1./exponent)


def compute_time_constant(knee):
    """Compute the characteristic time constant based on the knee value.

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


def compute_fwhm(std):
    """Compute the full-width half-max, given the gaussian standard deviation.

    Parameters
    ----------
    std : float
        Gaussian standard deviation.

    Returns
    -------
    float
        Calculated full-width half-max.
    """

    return 2 * np.sqrt(2 * np.log(2)) * std


def compute_gauss_std(fwhm):
    """Compute the gaussian standard deviation, given the full-width half-max.

    Parameters
    ----------
    fwhm : float
        Full-width half-max.

    Returns
    -------
    float
        Calculated standard deviation of a gaussian.
    """

    return fwhm / (2 * np.sqrt(2 * np.log(2)))
