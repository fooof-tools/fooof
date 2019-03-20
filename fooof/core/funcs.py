"""Function defintions for FOOOF.

NOTES
-----
- FOOOF currently (only) uses the exponential and gaussian functions.
- Linear & Quadratic functions are from previous versions of FOOOF.
    - There are left available for easy swapping back in, if desired.
"""

import numpy as np

###################################################################################################
###################################################################################################

def gaussian_function(xs, *params):
    """Gaussian function to use for fitting.

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

    for ii in range(0, len(params), 3):

        ctr, hgt, wid = params[ii:ii+3]

        ys = ys + hgt * np.exp(-(xs-ctr)**2 / (2*wid**2))

    return ys


def expo_function(xs, *params):
    """Exponential function to use for fitting 1/f, with a 'knee'.

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

    ys = np.zeros_like(xs)

    offset, knee, exp = params

    ys = ys + offset - np.log10(knee + xs**exp)

    return ys


def expo_nk_function(xs, *params):
    """Exponential function to use for fitting 1/f, with no 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (a, c) that define Lorentzian function:
        y = 10^off * (1/(x^exp))
        a: constant; c: slope past knee

    Returns
    -------
    ys : 1d array
        Output values for exponential (no-knee) function.
    """

    ys = np.zeros_like(xs)

    offset, exp = params

    ys = ys + offset - np.log10(xs**exp)

    return ys


def linear_function(xs, *params):
    """Linear function to use for quick fitting 1/f to estimate parameters.

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

    ys = np.zeros_like(xs)

    offset, slope = params

    ys = ys + offset + (xs*slope)

    return ys


def quadratic_function(xs, *params):
    """Quadratic function to use for better fitting 1/f.

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

    ys = np.zeros_like(xs)

    offset, slope, curve = params

    ys = ys + offset + (xs*slope) + ((xs**2)*curve)

    return ys


def get_ap_func(aperiodic_mode):
    """Select and return specified function for fitting aperiodic component.

    Parameters
    ----------
    aperiodic_mode : {'fixed', 'knee'}
        Which aperiodic fitting function to return.

    Returns
    -------
    ap_func : function
        Function for the aperiodic process.
    """

    if aperiodic_mode == 'fixed':
        ap_func = expo_nk_function
    elif aperiodic_mode == 'knee':
        ap_func = expo_function
    else:
        raise ValueError('Aperiodic mode not understood.')

    return ap_func


def infer_ap_func(aperiodic_params):
    """Infers which aperiodic function was used, from parameters.

    Parameters
    ----------
    aperiodic_params : list of float
        Parameters that describe the aperiodic component of a power spectrum.

    Returns
    -------
    aperiodic_mode : {'fixed', 'knee'}
        Which kind of aperiodic fitting function parameters are consistent with.
    """

    if len(aperiodic_params) == 2:
        aperiodic_mode = 'fixed'
    elif len(aperiodic_params) == 3:
        aperiodic_mode = 'knee'
    else:
        raise ValueError('Aperiodic parameters not consistent with any available option.')

    return aperiodic_mode
