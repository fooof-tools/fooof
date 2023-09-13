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

    Notes
    -----
    The knee frequency is an estimate of the frequency in spectrum at which the spectrum
    moves from the plateau region to the exponential decay.

    This approach for estimating the knee frequency comes from [1]_ (see [2]_ for code).

    Note that this provides an estimate of the knee frequency, but is not, in the general case,
    a precisely defined value. In particular, this conversion is based on the case of a Lorentzian
    with exponent = 2, and for other exponent values provides a non-exact approximation.

    References
    ----------
    .. [1] Gao, R., van den Brink, R. L., Pfeffer, T., & Voytek, B. (2020). Neuronal timescales
           are functionally dynamic and shaped by cortical microarchitecture. Elife, 9, e61277.
           https://doi.org/10.7554/eLife.61277
    .. [2] https://github.com/rdgao/field-echos/blob/master/echo_utils.py#L64
    """

    return knee ** (1. / exponent)


def compute_time_constant(knee_freq):
    """Compute the characteristic time constant from the estimated knee frequency.

    Parameters
    ----------
    knee_freq : float
        Estimated knee frequency.

    Returns
    -------
    float
        Calculated time constant value, tau, given the knee frequency.

    Notes
    -----
    This approach for estimating the time constant comes from [1]_ (see [2]_ for code).

    References
    ----------
    .. [1] Gao, R., van den Brink, R. L., Pfeffer, T., & Voytek, B. (2020). Neuronal timescales
           are functionally dynamic and shaped by cortical microarchitecture. Elife, 9, e61277.
           https://doi.org/10.7554/eLife.61277
    .. [2] https://github.com/rdgao/field-echos/blob/master/echo_utils.py#L65
    """

    return 1. / (2 * np.pi * knee_freq)


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
