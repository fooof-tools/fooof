"""Functionality to compute model goodness of fit."""

from inspect import isfunction

import numpy as np

###################################################################################################
###################################################################################################

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


# Collect available goodness of fit functions together
GOF_FUNCS = {
    'r_squared' : compute_r_squared,
    'adj_r_squared' : compute_adj_r_squared,
}


def compute_gof(power_spectrum, modeled_spectrum, gof_metric='r_squared'):
    """Compute goodness of fit between a model and a power spectrum.

    Parameters
    ----------
    power_spectrum : 1d array
        Real data power spectrum.
    modeled_spectrum : 1d array
        Modelled power spectrum.
    gof_metric : {'r_squared', 'adj_r_squared'} or callable
        Which approach to take to compute the goodness of fit.

    Returns
    -------
    gof : float
        Computed goodness of fit.
    """

    if isinstance(gof_metric, str):
        gof = GOF_FUNCS[gof_metric.lower()](power_spectrum, modeled_spectrum)
    elif isfunction(gof_metric):
        gof = gof_metric(power_spectrum, modeled_spectrum)

    return gof
