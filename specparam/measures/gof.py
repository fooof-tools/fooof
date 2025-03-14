"""Goodness of fit related functions & utilities."""

from inspect import isfunction

import numpy as np

###################################################################################################
###################################################################################################

## Goodness of fit measures

def compute_r_squared(power_spectrum, modeled_spectrum):
    """Calculate the r-squared of the model, compared to the original data.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.

    Returns
    -------
    r_squared : float
        R-squared of the model fit.
    """

    corrcoefs = np.corrcoef(power_spectrum, modeled_spectrum)
    r_squared = corrcoefs[0][1] ** 2

    return r_squared


def compute_adj_r_squared(power_spectrum, modeled_spectrum, n_params):
    """Calculate the adjusted r-squared of the model, compared to the original data.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.

    Returns
    -------
    adj_r_squared : float
        Adjusted R-squared of the model fit.
    """

    n_points = len(power_spectrum)
    r_squared = compute_r_squared(power_spectrum, modeled_spectrum)
    adj_r_squared = 1 - (1 - r_squared) * (n_points - 1) / (n_points - n_params - 1)

    return adj_r_squared


# Collect available error functions together
RSQUARED_FUNCS = {
    'r_squared' : compute_r_squared,
    'adj_r_squared' : compute_adj_r_squared,
}


## ERROR FUNCTIONS

def compute_mean_abs_error(power_spectrum, modeled_spectrum):
    """Compute mean absolute error.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.

    Returns
    -------
    error : float
        Computed mean absolute error.
    """

    error = np.abs(power_spectrum - modeled_spectrum).mean()

    return error


def compute_mean_squared_error(power_spectrum, modeled_spectrum):
    """Compute mean squared error.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.

    Returns
    -------
    error : float
        Computed mean squared error.
    """

    error = ((power_spectrum - modeled_spectrum) ** 2).mean()

    return error


def compute_root_mean_squared_error(power_spectrum, modeled_spectrum):
    """Compute root mean squared error.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.

    Returns
    -------
    error : float
        Computed root mean squared error.
    """

    error = np.sqrt(((power_spectrum - modeled_spectrum) ** 2).mean())

    return error


def compute_median_abs_error(power_spectrum, modeled_spectrum):
    """Calculate the median absolute error.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.

    Returns
    -------
    error : float
        Computed median absolute error.
    """

    error = np.median(np.abs(modeled_spectrum - power_spectrum), axis=0)

    return error


# Collect available error functions together
ERROR_FUNCS = {
    'mae' : compute_mean_abs_error,
    'mse' : compute_mean_squared_error,
    'rmse' : compute_root_mean_squared_error,
    'medae' : compute_median_abs_error,
}


def compute_error(power_spectrum, modeled_spectrum, error_metric='mae'):
    """Compute error between a model and a power spectrum.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.
    error_metric : {'mae', 'mse', 'rsme', 'medae'} or callable
        Which approach to take to compute the error.

    Returns
    -------
    error : float
        Computed error.
    """

    if isinstance(error_metric, str):
        error = ERROR_FUNCS[error_metric.lower()](power_spectrum, modeled_spectrum)
    elif isfunction(error_metric):
        error = error_metric(power_spectrum, modeled_spectrum)

    return error
