"""Function defintions for FOOOF."""

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

        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]

        y = y + amp * np.exp(-(x-ctr)**2 / (2*wid**2))

    return y


def loglorentzian_function(x, *params):
    """Log-Lorentzian function to use for better fitting 1/f.

    NOTE: this function requires linear frequency (not log) and all parameters
    should be positive since function operates in log-Y domain

    Parameters
    ----------
    x : 1d array
        Input x-axis values.
    *params : float
        Parameters (a, b, c) that define Lorentzian function:
        y = 10^a * (1/(b + x^c))
        a: constant; b: knee^2; c: slope past knee

    Returns
    -------
    y : 1d array
        Output values for quadratic function.
    """

    y = np.zeros_like(x)
    a, b, c = params
    y = a - np.log10(b + x**c)

    return y