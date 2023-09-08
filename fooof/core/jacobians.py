""""Functions for computing Jacobian matrices to be used during fitting.

Notes
-----
These functions line up with those in `funcs`.
The parameters in these functions are labelled {a, b, c, ...}, but follow the order in `funcs`.
These functions are designed to be passed into `curve_fit` to provide a computed Jacobian.
"""

import numpy as np

###################################################################################################
###################################################################################################

## Periodic fit functions

def jacobian_gauss(xs, *params):
    """Create the Jacobian matrix for the Guassian function.

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

    jacobians = np.zeros((len(xs), len(params)))

    for i, (a, b, c) in enumerate(zip(*[iter(params)] * 3)):

        ax = -a + xs
        ax2 = ax**2

        c2 = c**2
        c3 = c**3

        exp = np.exp(-ax2 / (2 * c2))
        exp_b = exp * b

        ii = i * 3
        jacobians[:, ii] = (exp_b * ax) / c2
        jacobians[:, ii+1] = exp
        jacobians[:, ii+2] = (exp_b * ax2) / c3

    return jacobians


## Aperiodic fit functions

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
    jacobian = np.hstack([
        np.ones([len(xs), 1]),
        - (1 / (b + xs**c)).reshape(-1, 1),
        -((xs**c * np.log10(xs)) / (b + xs**c)).reshape(-1, 1),
    ])

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

    jacobian = np.hstack([
        np.ones([len(xs), 1]),
        (-np.log10(xs) / np.log10(10)).reshape(-1, 1),
    ])

    return jacobian
