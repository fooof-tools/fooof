"""Functionality to compute model error."""

from inspect import isfunction

import numpy as np

###################################################################################################
###################################################################################################

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


def compute_error(power_spectrum, modeled_spectrum, error_metric='mae', **kwargs):
    """Compute error between a model and a power spectrum.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.
    error_metric : {'mae', 'mse', 'rsme', 'medae'} or callable
        Which approach to take to compute the error.
    **kwargs
        Additional keyword arguments for the error function.

    Returns
    -------
    error : float
        Computed error.
    """

    if isinstance(error_metric, str):
        error_func = ERROR_FUNCS[error_metric.lower()]
    elif isfunction(error_metric):
        error_func = error_metric

    return error_func(power_spectrum, modeled_spectrum, **kwargs)
