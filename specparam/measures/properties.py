"""Compute properties of data."""

from inspect import isfunction

import numpy as np
from scipy.stats import sem

###################################################################################################
###################################################################################################

## COLLECT MEASURES

AVG_FUNCS = {
    'mean' : np.mean,
    'median' : np.median,
    'nanmean' : np.nanmean,
    'nanmedian' : np.nanmedian,
}

DISPERSION_FUNCS = {
    'var' : np.var,
    'nanvar' : np.nanvar,
    'std' : np.std,
    'nanstd' : np.nanstd,
    'sem' : sem,
}

## FUNCTIONS

def compute_average(data, average='mean'):
    """Compute the average across an array of data.

    Parameters
    ----------
    data : 2d array
        Data to compute average across.
        Average is computed across the 0th axis.
    average : {'mean', 'median'} or callable
        Which approach to take to compute the average.

    Returns
    -------
    avg_data : 1d array
        Average across given data array.
    """

    if isinstance(average, str) and data.ndim == 2:
        avg_data = AVG_FUNCS[average](data, axis=0)
    elif isfunction(average) and data.ndim == 2:
        avg_data = average(data)
    else:
        avg_data = data

    return avg_data


def compute_dispersion(data, dispersion='std'):
    """Compute the dispersion across an array of data.

    Parameters
    ----------
    data : 2d array
        Data to compute dispersion across.
        Dispersion is computed across the 0th axis.
    dispersion : {'var', 'std', 'sem'}
        Which approach to take to compute the dispersion.

    Returns
    -------
    dispersion_data : 1d array
        Dispersion across given data array.
    """

    if isinstance(dispersion, str):
        dispersion_data = DISPERSION_FUNCS[dispersion](data, axis=0)
    elif isfunction(dispersion):
        dispersion_data = dispersion(data)
    else:
        dispersion_data = data

    return dispersion_data


def compute_presence(data, average=False, output='ratio'):
    """Compute data presence (as number of non-NaN values) from an array of data.

    Parameters
    ----------
    data : 1d or 2d array
        Data array to check presence of.
    average : bool, optional, default: False
        Whether to average across elements. Only used for 2d array inputs.
        If False, for 2d array, output is an array with length of the 0th dimension of the input.
        If True, for 2d arrays, output is a single value averaged across the whole array.
    output : {'ratio', 'percent'}
        Representation for the output:
            'ratio' - ratio value, between 0.0, 1.0.
            'percent' - percent value, betweeon 0-100%.

    Returns
    -------
    presence : float or array of float
        The computed presence in the given array.
    """

    assert output in ['ratio', 'percent'], 'Setting for output type not understood.'

    if data.ndim == 1 or average:
        presence = np.sum(~np.isnan(data)) / data.size

    elif data.ndim == 2:
        presence = np.sum(~np.isnan(data), 0) / (np.ones(data.shape[1]) * data.shape[0])

    if output == 'percent':
        presence *= 100

    return presence
