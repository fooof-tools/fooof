"""Functions that can be used for model fitting."""

import numpy as np
from scipy.special import erf

from specparam.utils.array import normalize

###################################################################################################
###################################################################################################

## PEAK FUNCTIONS

def gaussian_function(xs, *params):
    """Gaussian fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define gaussian function.

    Returns
    -------
    ys : 1d array
        Output values for gaussian function.
    """

    ys = np.zeros_like(xs)

    for ctr, hgt, wid in zip(*[iter(params)] * 3):

        ys = ys + hgt * np.exp(-(xs-ctr)**2 / (2*wid**2))

    return ys


def skewed_gaussian_function(xs, *params):
    """Skewed gaussian fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define the skewed normal distribution function.

    Returns
    -------
    ys : 1d array
        Output values for skewed normal distribution function.
    """

    ys = np.zeros_like(xs)

    for ii in range(0, len(params), 4):

        ctr, hgt, wid, skew = params[ii:ii+4]

        ts = (xs - ctr) / wid
        temp = 2 / wid * (1 / np.sqrt(2 * np.pi) * np.exp(-ts**2 / 2)) * \
            ((1 + erf(skew * ts / np.sqrt(2))) / 2)
        ys = ys + hgt * normalize(temp)

    return ys


def cauchy_function(xs, *params):
    """Cauchy fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define a cauchy function.

    Returns
    -------
    ys : 1d array
        Output values for cauchy function.
    """

    ys = np.zeros_like(xs)

    for ctr, hgt, wid in zip(*[iter(params)] * 3):

        ys = ys + hgt*wid**2/((xs-ctr)**2+wid**2)

    return ys


## APERIODIC FUNCTIONS

def expo_function(xs, *params):
    """Exponential function, for fitting aperiodic component with a 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, knee, exp) that define Lorentzian function:
        y = 10^offset * (1/(knee + x^exp))

    Returns
    -------
    ys : 1d array
        Output values for exponential function.
    """

    offset, knee, exp = params
    ys = offset - np.log10(knee + xs**exp)

    return ys


def expo_nk_function(xs, *params):
    """Exponential function, for fitting aperiodic component without a 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, exp) that define Lorentzian function:
        y = 10^off * (1/(x^exp))

    Returns
    -------
    ys : 1d array
        Output values for exponential function, without a knee.
    """

    offset, exp = params
    ys = offset - np.log10(xs**exp)

    return ys


def double_expo_function(xs, *params):
    """Double exponential function, for fitting aperiodic component with two exponents and a knee.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, exp0, knee, exp1) that define the function:
        y = 10^offset * (1/((x**exp0) * (knee + x^exp1))

    Returns
    -------
    ys : 1d array
        Output values for exponential function.
    """

    ys = np.zeros_like(xs)

    offset, exp0, knee, exp1 = params

    ys = ys + offset - np.log10((xs**exp0) * (knee + xs**exp1))

    return ys


def linear_function(xs, *params):
    """Linear fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define linear function.

    Returns
    -------
    ys : 1d array
        Output values for linear function.
    """

    offset, slope = params
    ys = offset + (xs*slope)

    return ys


def quadratic_function(xs, *params):
    """Quadratic fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define quadratic function.

    Returns
    -------
    ys : 1d array
        Output values for quadratic function.
    """

    offset, slope, curve = params
    ys = offset + (xs*slope) + ((xs**2)*curve)

    return ys
