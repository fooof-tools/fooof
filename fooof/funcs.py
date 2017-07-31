"""Function defintions for FOOOF."""

import numpy as np

###################################################################################################
###################################################################################################

def gaussian_function(x, *params):
    """Gaussian function to use for fitting.

    Parameters
    ----------
    x :
        xx
    *params :
        xx

    Returns
    -------
    y :
        xx
    """

    y = np.zeros_like(x)

    for i in range(0, len(params), 3):

        ctr = params[i]
        amp = params[i+1]
        wid = params[i+2]

        y = y + amp * np.exp(-((x - ctr)/wid)**2)

    return y


def linear_function(x, *params):
    """Linear function to use for quick fitting 1/f to estimate parameters.

    Parameters
    ----------
    x :
        xx
    *params :
        xx

    Returns
    -------
    y :
        xx
    """

    y = np.zeros_like(x)

    offset = params[0]
    slope = params[1]

    y = y + offset + (x*slope)

    return y


def quadratic_function(x, *params):
    """Quadratic function to use for better fitting 1/f.

    Parameters
    ----------
    x :
        xx
    *params :
        xx

    Returns
    -------
    y :
        xx
    """

    xs = 1

    y = np.zeros_like(x)

    offset = params[0]
    slope = params[1]
    curve = params[2]

    y = y + offset + (x*slope) + ((x**2)*curve)

    return y
