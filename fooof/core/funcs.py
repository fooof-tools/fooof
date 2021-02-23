"""Functions that can be used for model fitting.

NOTES
-----
- FOOOF currently (only) uses the exponential and gaussian functions.
- Linear & Quadratic functions are from previous versions of FOOOF.
    - They are left available for easy swapping back in, if desired.
"""

from inspect import isfunction

import numpy as np

from fooof.core.errors import InconsistentDataError

###################################################################################################
###################################################################################################

def gaussian_function(xs, cf, pw, bw, *params):
    """Gaussian fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    cf : float
        The center of the gaussian.
    pw : float
        The height of the gaussian.
    bw : float
        The width of the gaussian.
    *params : float
        Additional centers, heights, and widths.

    Returns
    -------
    ys : 1d array
        Output values for gaussian function.
    """

    ys = np.zeros_like(xs)

    params = [cf, pw, bw, *params]

    for ii in range(0, len(params), 3):

        ctr, hgt, wid = params[ii:ii+3]
        ys = ys + hgt * np.exp(-(xs-ctr)**2 / (2*wid**2))

    return ys


def expo_function(xs, offset, knee, exp):
    """Exponential fitting function, for fitting aperiodic component with a 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    offset : float
        The y-intercept of the fit.
    knee : float
        The bend in the fit.
    exp : float
        The exponential slope of the fit.

    Returns
    -------
    ys : 1d array
        Output values for exponential function.

    Notes
    -----
    Parameters (offset, knee, exp) that define Lorentzian function:
    y = 10^offset * (1/(knee + x^exp))
    """

    ys = np.zeros_like(xs)

    ys = ys + offset - np.log10(knee + xs**exp)

    return ys


def expo_nk_function(xs, offset, exp):
    """Exponential fitting function, for fitting aperiodic component without a 'knee'.

    NOTE: this function requires linear frequency (not log).

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    offset : float
        The y-intercept of the fit.
    exp : float
        The exponential slope of the fit.

    Returns
    -------
    ys : 1d array
        Output values for exponential function, without a knee.

    Notes
    -----
    Parameters (offset, exp) that define Lorentzian function:
    y = 10^off * (1/(x^exp))
    """

    ys = np.zeros_like(xs)

    ys = ys + offset - np.log10(xs**exp)

    return ys


def linear_function(xs, offset, slope):
    """Linear fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    offset : float
        The y-intercept of the fit.
    slope : float
        The slope of the fit.

    Returns
    -------
    ys : 1d array
        Output values for linear function.
    """

    ys = np.zeros_like(xs)

    ys = ys + offset + (xs*slope)

    return ys


def quadratic_function(xs, offset, slope, curve):
    """Quadratic fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    offset : float
        The y-intercept of the fit.
    slope : float
        The slope of the fit.
    curve : float
        The curve of the fit.

    Returns
    -------
    ys : 1d array
        Output values for quadratic function.
    """

    ys = np.zeros_like(xs)

    ys = ys + offset + (xs*slope) + ((xs**2)*curve)

    return ys


def get_pe_func(periodic_mode):
    """Select and return specified function for periodic component.

    Parameters
    ----------
    periodic_mode : {'gaussian'}
        Which periodic fitting function to return.

    Returns
    -------
    pe_func : function
        Function for the periodic component.

    Raises
    ------
    ValueError
        If the specified periodic mode label is not understood.

    """

    if isfunction(periodic_mode):
        pe_func = periodic_mode
    elif periodic_mode == 'gaussian':
        pe_func = gaussian_function
    else:
        raise ValueError("Requested periodic mode not understood.")

    return pe_func


def get_ap_func(aperiodic_mode):
    """Select and return specified function for aperiodic component.

    Parameters
    ----------
    aperiodic_mode : {'fixed', 'knee'}
        Which aperiodic fitting function to return.

    Returns
    -------
    ap_func : function
        Function for the aperiodic component.

    Raises
    ------
    ValueError
        If the specified aperiodic mode label is not understood.
    """

    if isfunction(aperiodic_mode):
        ap_func = aperiodic_mode
    elif aperiodic_mode == 'fixed':
        ap_func = expo_nk_function
    elif aperiodic_mode == 'knee':
        ap_func = expo_function
    else:
        raise ValueError("Requested aperiodic mode not understood.")

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
        Which kind of aperiodic fitting function the given parameters are consistent with.

    Raises
    ------
    InconsistentDataError
        If the given parameters are inconsistent with any available aperiodic function.
    """

    if len(aperiodic_params) == 2:
        aperiodic_mode = 'fixed'
    elif len(aperiodic_params) == 3:
        aperiodic_mode = 'knee'
    else:
        raise InconsistentDataError("The given aperiodic parameters are "
                                    "inconsistent with available options.")

    return aperiodic_mode
