"""Functions that can be used for model fitting.

Conventions:
- Each function in this file should be named as `{LABEL}_function`
- Each function takes as input:
    - `xs` : the input frequency vector
    - `*params` : a variable number of input parameters
        - For aperiodic functions, this is the number of input parameters for the function
        - For peak functions, this is the number of function parameters * n_peaks
- Each function should define the input parameters and function formula in the docstring
    - When defining a fit mode, this information should be consistent in the Mode object

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
        Each gaussian has 3 parameters: ctr, hgt, wid.

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
        Each skewed normal peak has 4 parameters: ctr, hgt, wid, skew.

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

    for ctr, hgt, wid, skew in zip(*[iter(params)] * 4):

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
        Each cauchy peak has 3 parameters: ctr, hgt, wid.

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
    r"""Gamma fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define a gamma function.
        Each gamma peak has 4 parameters: ctr, hgt, shape (shp), scale (scl).

    Returns
    -------
    ys : 1d array
        Output values for gamma function.

    Notes
    -----
    Defines a gamma fit function as:

        P(F)_n = a * \frac{1}{\Gamma (k)\theta^{k}}F_c^{k-1}e^{-\frac{F_c}{\theta}}

    where k is the shape parameter, theta is the scale parameter, and F_c is the
    frequency values scaled to center the peak at the desired center frequency.
    """

    ys = np.zeros_like(xs)

    for ctr, hgt, shp, scl in zip(*[iter(params)] * 4):
        cxs = xs-ctr
        cxs = cxs.clip(min=0)
        ys = ys + hgt * normalize((1 / (gamma(shp) * scl**shp) * cxs**(shp-1) * np.exp(-cxs/scl)))


def triangle_function(xs, *params):
    r"""Triangle fitting function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters that define a triangle function.
        Each triangle peak has 3 parameters: ctr, hgt, wid.

    Returns
    -------
    ys : 1d array
        Output values for triangle function.

    Notes
    -----
    Defines a triangular fit function as:

    .. math::

        \text{tri}(x) = \begin{cases} 1 - |x| & \text{if } |x| < 1 \\ 0 & \text{if } |x| \geq 1 \end{cases}

    To use this function as a peak function, this function is scaled by hgt and wid, and moved to ctr.
    """

    ys = np.zeros_like(xs)
    fres = xs[1] - xs[0]

    for ctr, hgt, wid in zip(*[iter(params)] * 3):

        n_samples = int(np.ceil(2 * wid / fres))
        n_samples += 1 if n_samples % 2 == 0 else 0
        temp = np.arccos(np.cos(np.linspace(0, 2 * np.pi, n_samples)))
        ys[np.abs(xs - ctr) <= (n_samples / 2) * fres] += hgt * normalize(temp)

    return ys


## APERIODIC FUNCTIONS

def powerlaw_function(xs, *params):
    r"""Powerlaw function, for fitting aperiodic component as 1/f.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters the powerlaw (1/f) function: offset, exponent.

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
        Parameters that define the Lorentzian function: offset, knee, exponent.

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
        Parameters that define the the double exponent function: offset, exp0, knee, exp1.

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
        Parameters that define the linear function: offset, slope.

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
        Parameters that define the quadratic function: offset, slope, curve.

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
