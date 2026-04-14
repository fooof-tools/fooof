"""Functions that can be used for model fitting.

For defining the formulas, the following standard variable definitions are used (formula / code):

- `F` / `xs` : frequency vector
- `a` / `ctr` : the height of a peak function, corresponding to 'power' (pw).
- `c` / `hgt` : the center of a peak function, corresponding to 'center frequency' (cf).
- `w` / `wid` : the width of a peak function, corresponding to 'bandwidth' (bw).
- `\chi` / `exp` : an exponent of a 1/f function. Can be subscripted if there are multiple.
- `k` / `knee` : a knee of a Lorentzian function. Can be subscripted if there are multiple.
- `b` / `offset` : the offset of an aperiodic function.
- `A` : relating to the aperiodic component.
- `P` : relating to the periodic component.
"""

from math import gamma

import numpy as np
from scipy.special import erf

from specparam.utils.array import normalize
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
        Parameters that define the gaussian function.

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

        ys = ys + hgt * np.exp(-(xs - ctr)**2 / (2 * wid**2))

    return ys


def skewed_gaussian_function(xs, *params):
    r"""Skewed gaussian fitting function.

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
    Defines a skewed Gaussian fit function as:

    .. math::

        P(F)_n = a * \frac{2}{w\sqrt{2\pi}} e^{-\frac{(F - \epsilon)^2} {2w^2}} * 0.5 * (1 + erf(k + \frac{F - c}{w\sqrt{2}})

    where `k` is the skew factor, and `erf` is the error function.
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
    r"""Cauchy fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define the cauchy function.

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


def gamma_function(xs, *params):
    """Gamma fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define a gamma function.

    Returns
    -------
    ys : 1d array
        Output values for gamma function.

    Notes
    -----
    Parameters should come in ordered sets of 4, each including the following:

    - cf: center frequency parameter
    - pw: power (height) parameter
    - shp: shape parameter
    - scl: scale parameter
    """

    ys = np.zeros_like(xs)

    for ctr, hgt, shp, scale in zip(*[iter(params)] * 4):
        cxs = xs-ctr
        cxs = cxs.clip(min=0)
        ys = ys + hgt * normalize((1 / (gamma(shp) * scale**shp) * cxs**(shp-1) * np.exp(-cxs/scale)))

    return ys


## APERIODIC FUNCTIONS

def powerlaw_function(xs, *params):
    r"""Powerlaw function, for fitting aperiodic component as 1/f.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, exponent) that define the 1/f function.

    Returns
    -------
    ys : 1d array
        Output values for exponential function.

    Notes
    -----
    This is an aperiodic fit function, defined for use with LINEAR freqs and LOG power.

    Defines a 1/f fit function as:

    .. math::

        A(F) = 10^b * \frac{1}{F^\chi}

    Note that the above function form is defined in linear/linear space.
    The equivalent for linear/log, as implemented in the code, is:

    .. math::

        A(F) = b - \log(F^\chi)
    """

    offset, exp = params
    ys = offset - np.log10(xs**exp)

    return ys


def lorentzian_function(xs, *params):
    r"""Lorentzian function, for fitting aperiodic component as a 1/f function with a knee.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, knee, exponent) that define the Lorentzian function.

    Returns
    -------
    ys : 1d array
        Output values for exponential function.

    Notes
    -----
    This is an aperiodic fit function, defined for use with LINEAR freqs and LOG power.

    Defines a Lorentzian fit function as:

    .. math::

        A(F) = 10^b * \frac{1}{(k + F^\chi)}

    Note that the above function form is defined in linear/linear space.
    The equivalent for linear/log, as implemented in the code, is:

    .. math::

        A(F) = b - \log(k + F^\chi)
    """

    offset, knee, exp = params
    ys = offset - np.log10(knee + xs**exp)

    return ys


def double_expo_function(xs, *params):
    r"""Double exponential function, for fitting aperiodic component with two exponents and a knee.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters (offset, exp0, knee, exp1) that define the the double exponent function.

    Returns
    -------
    ys : 1d array
        Output values for exponential function.

    Notes
    -----
    This is an aperiodic fit function, defined for use with LINEAR freqs and LOG power.

    Defines a double-exponent 1/f fit function as:

    .. math::

        A(F) = 10^b * \frac{1}{F^{\chi_{0}} * (k + F^{\chi_{1}})}

    Note that the above function form is defined in linear/linear space.
    The equivalent for linear/log, as implemented in the code, is:

    .. math::

        A(F) = b - \log(F^{\chi_{0}} * (k + F^{\chi_{1}}))
    """

    ys = np.zeros_like(xs)

    offset, exp0, knee, exp1 = params

    ys = ys + offset - np.log10((xs**exp0) * (knee + xs**exp1))

    return ys


def linear_function(xs, *params):
    r"""Linear fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define the linear function.

    Returns
    -------
    ys : 1d array
        Output values for linear function.

    Notes
    -----
    This is an aperiodic fit function, defined for use with LOG freqs and LOG power.

    Defines a linear fit function as:

    .. math::

        A(F) = b + \chi * F
    """

    offset, slope = params
    ys = offset + (xs*slope)

    return ys


def quadratic_function(xs, *params):
    r"""Quadratic fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define the quadratic function.

    Returns
    -------
    ys : 1d array
        Output values for quadratic function.

    Notes
    -----
    This is an aperiodic fit function.

    Defines a quaratic fit function as:

    .. math::

        A(F) = b + \chi * F + F^2 * v
    """

    offset, slope, curve = params
    ys = offset + (xs*slope) + ((xs**2)*curve)

    return ys
