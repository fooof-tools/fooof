"""Functions that can be used for model fitting.


For defining the formulas, the following standard variable definitions are used (formula / code):
- `F` / `xs` : frequency vector
- `a` / `ctr` : the height of a peak function, corresponding to 'power' (pw).
- `c` / `hgt` : the center of a peak function, corresponding to 'center frequency' (cf).
- `w` / `wid` : the width of a peak function, corresponding to 'bandwidth' (bw).
- `\chi` / `exp` : an exponent of a 1/f function. Can be subscripted if there are multiple.
- `k` / `knee` : a knee of a Lorentzian function. Can be subscripted if there are multiple.
- `b` / `offset` : the offset of an aperiodic function.
"""

import numpy as np
from scipy.special import erf

from specparam.utils.array import normalize

###################################################################################################
###################################################################################################

## PEAK FUNCTIONS

def gaussian_function(xs, *params):
    r"""Gaussian fitting function.

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

    Notes
    -----
    Defines a Gaussian fit function as:

    .. math::

        P(F)_n = a * \frac {w^2} {(F - c)^2 + w^2}
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

    Notes
    -----
    Defines a skewed Gaussian fit function as (TODO - check & fix):

    .. math::

        P(F)_n = a * \frac{2}{w\sqrt{2\pi}} e^{\frac{(F - \epsilon)^2} {2w^2}}
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

    Notes
    -----
    Defines a cauchy fit function as:

    .. math::

        P(F)_n = a * \frac {w^2} {(F - c)^2 + w^2}
    """

    ys = np.zeros_like(xs)

    for ctr, hgt, wid in zip(*[iter(params)] * 3):

        ys = ys + hgt * wid**2 / ((xs - ctr)**2 + wid**2)

    return ys


## APERIODIC FUNCTIONS

def expo_function(xs, *params):
    """Exponential function, for fitting aperiodic component with a 'knee'.

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

    Notes
    -----
    This is an aperiodic fit function, defined for use with LINEAR freqs and LOG power.

    Defines a 1/f fit function as:

    .. math::

        AP(F) = 10^b * \frac{1}{F^\chi}

    Note that the above function form is defined in linear/linear space.
    The equivalent for linear/log, as implemented in the code, is:

    .. math::

        AP(F) = b - \log(F^\chi)
    """

    offset, knee, exp = params
    ys = offset - np.log10(knee + xs**exp)

    return ys


def expo_nk_function(xs, *params):
    """Exponential function, for fitting aperiodic component without a 'knee'.

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

    Notes
    -----
    This is an aperiodic fit function, defined for use with LINEAR freqs and LOG power.

    Defines a Lorentzian fit function as:

    .. math::

        AP(F) = 10^b * \frac{1}{(k + F^\chi)}

    Note that the above function form is defined in linear/linear space.
    The equivalent for linear/log, as implemented in the code, is:

    .. math::

        A(F) = b - \log(k + F^\chi)
    """

    offset, exp = params
    ys = offset - np.log10(xs**exp)

    return ys


def double_expo_function(xs, *params):
    """Double exponential function, for fitting aperiodic component with two exponents and a knee.

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

    Notes
    -----
    This is an aperiodic fit function, defined for use with LINEAR freqs and LOG power.

    Defines a double-exponent 1/f fit function as:

    .. math::

        AP(F) = 10^b * \frac{1}{F^{\chi_{0}} * (k + F^{\chi_{1}})}

    Note that the above function form is defined in linear/linear space.
    The equivalent for linear/log, as implemented in the code, is:

    .. math::

        AP(F) = b - \log(F^{\chi_{0}} * (k + F^{\chi_{1}}))
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

    Notes
    -----
    This is an aperiodic fit function, defined for use with LOG freqs and LOG power.

    Defines a linear fit function as:

    .. math::

        AP(F) = b + \chi * F
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

    Notes
    -----
    This is an aperiodic fit function.

    Defines a quaratic fit function as:

    .. math::

        AP(F) = b + \chi * F + F^2 * v
    """

    offset, slope, curve = params
    ys = offset + (xs*slope) + ((xs**2)*curve)

    return ys
