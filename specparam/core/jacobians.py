""""Functions for computing Jacobian matrices to be used during fitting.

Notes
-----
These functions line up with those in `funcs`.
The parameters in these functions are labeled {a, b, c, ...}, but follow the order in `funcs`.
These functions are designed to be passed into `curve_fit` to provide a computed Jacobian.
"""

import numpy as np

###################################################################################################
###################################################################################################

## Periodic Jacobian functions

def jacobian_gauss(xs, *params):
    """Create the Jacobian matrix for the Gaussian function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters for the function.

    Returns
    -------
    jacobian : 2d array
        Jacobian matrix, with shape [len(xs), n_params].
    """

    jacobian = np.zeros((len(xs), len(params)))

    for i, (a, b, c) in enumerate(zip(*[iter(params)] * 3)):

        ax = -a + xs
        ax2 = ax**2

        c2 = c**2
        c3 = c**3

        exp = np.exp(-ax2 / (2 * c2))
        exp_b = exp * b

        ii = i * 3
        jacobian[:, ii] = (exp_b * ax) / c2
        jacobian[:, ii+1] = exp
        jacobian[:, ii+2] = (exp_b * ax2) / c3

    return jacobian


## Aperiodic Jacobian functions

def jacobian_expo(xs, *params):
    """Create the Jacobian matrix for the exponential function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters for the function.

    Returns
    -------
    jacobian : 2d array
        Jacobian matrix, with shape [len(xs), n_params].
    """

    a, b, c = params

    xs_c = xs**c
    b_xs_c = xs_c + b

    jacobian = np.ones((len(xs), len(params)))
    jacobian[:, 1] = -1 / b_xs_c
    jacobian[:, 2] = -(xs_c * np.log10(xs)) / b_xs_c

    return jacobian


def jacobian_expo_nk(xs, *params):
    """Create the Jacobian matrix for the exponential no-knee function.

    Parameters
    ----------
    xs : 1d array
        Input x-axis values.
    *params : float
        Parameters for the function.

    Returns
    -------
    jacobian : 2d array
        Jacobian matrix, with shape [len(xs), n_params].
    """

    jacobian = np.ones((len(xs), len(params)))
    jacobian[:, 1] = -np.log10(xs)

    return jacobian
