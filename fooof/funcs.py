"""Function defintions for FOOOF.

NOTES
-----
- FOOOF currently (only) uses the exponential and gaussian functions.
- Linear & Quadratic functions are from previous version, left in for easy swapping back if desired.
"""

import numpy as np

###################################################################################################
###################################################################################################

def gaussian_function(x, *params):
    """Gaussian function to use for fitting.

    Parameters
    ----------
    x : 1d array
        Input x-axis values.
    *params : float
        Parameters that define gaussian function.

    Returns
    -------
    y : 1d array
        Output values for gaussian function.
    """

    y = np.zeros_like(x)

    for i in range(0, len(params), 3):

        ctr, amp, wid = params[i:i+3]

        y = y + amp * np.exp(-(x-ctr)**2 / (2*wid**2))

    return y


def expo_function(x, *params):
    """Exponential function to use for fitting 1/f, with a 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    x : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, knee, exp) that define Lorentzian function:
        y = 10^offset * (1/(knee + x^exp))

    Returns
    -------
    y : 1d array
        Output values for quadratic function.
    """

    y = np.zeros_like(x)

    offset, knee, exp = params

    y = y + offset - np.log10(knee + x**exp)

    return y


def expo_nk_function(x, *params):
    """Exponential function to use for fitting 1/f, with no 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    x : 1d array
        Input x-axis values.
    *params : float
        Parameters (a, c) that define Lorentzian function:
        y = 10^off * (1/(x^exp))
        a: constant; c: slope past knee

    Returns
    -------
    y : 1d array
        Output values for quadratic function.
    """

    y = np.zeros_like(x)

    offset, exp = params

    y = y + offset - np.log10(x**exp)

    return y


def linear_function(x, *params):
    """Linear function to use for quick fitting 1/f to estimate parameters.

    Parameters
    ----------
    x : 1d array
        Input x-axis values.
    *params : float
        Parameters that define linear function.

    Returns
    -------
    y : 1d array
        Output values for linear function.
    """

    y = np.zeros_like(x)

    offset, slope = params

    y = y + offset + (x*slope)

    return y


def quadratic_function(x, *params):
    """Quadratic function to use for better fitting 1/f.

    Parameters
    ----------
    x : 1d array
        Input x-axis values.
    *params : float
        Parameters that define quadratic function.

    Returns
    -------
    y : 1d array
        Output values for quadratic function.
    """

    y = np.zeros_like(x)

    offset, slope, curve = params

    y = y + offset + (x*slope) + ((x**2)*curve)

    return y
