"""Functions to analyze and investigate ERPparam results - model fit error."""

import numpy as np

from ERPparam.sim.gen import gen_periodic
from ERPparam.plts.error import plot_spectral_error
from ERPparam.core.errors import NoModelError, NoDataError

###################################################################################################
###################################################################################################

def compute_pointwise_error_fm(fm, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the time-point by time-point error of a model fit from a ERPparam object.

    Parameters
    ----------
    fm : ERPparam
        Object containing the data and model.
    plot_errors : bool, optional, default: True
        Whether to plot the errors across frequencies.
    return_errors : bool, optional, default: False
        Whether to return the calculated errors.
    **plt_kwargs
        Keyword arguments to be passed to the plot function.

    Returns
    -------
    errors : 1d array
        Calculated values of the difference between the data and the model.
        Only returned if `return_errors` is True.

    Raises
    ------
    NoDataError
        If there is no data available to calculate model error from.
    NoModelError
        If there are no model results available to calculate model error from.
    """

    if not fm.has_data:
        raise NoDataError("Data must be available in the object to calculate errors.")
    if not fm.has_model:
        raise NoModelError("No model is available to use, can not proceed.")

    errors = compute_pointwise_error(fm._peak_fit, fm.signal)

    if plot_errors:
        plot_spectral_error(fm.time, errors, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error_fg(fg, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the time-point by time-point error of model fits from a ERPparamGroup object.

    Parameters
    ----------
    fg : ERPparamGroup
        Object containing the data and models.
    plot_errors : bool, optional, default: True
        Whether to plot the errors across frequencies.
    return_errors : bool, optional, default: False
        Whether to return the calculated errors.
    **plt_kwargs
        Keyword arguments to be passed to the plot function.

    Returns
    -------
    errors : 2d array
        Calculated values of the difference between the data and the models.
        Only returned if `return_errors` is True.

    Raises
    ------
    NoDataError
        If there is no data available to calculate model errors from.
    NoModelError
        If there are no model results available to calculate model errors from.
    """

    if not np.any(fg.signal):
        raise NoDataError("Data must be available in the object to calculate errors.")
    if not fg.has_model:
        raise NoModelError("No model is available to use, can not proceed.")

    errors = np.zeros_like(fg.signal)

    for ind, (res, data) in enumerate(zip(fg, fg.signal)):

        model = gen_periodic(fg.time, res.gaussian_params)
        errors[ind, :] = np.abs(model - data)

    mean = np.mean(errors, 0)
    standard_dev = np.std(errors, 0)

    if plot_errors:
        plot_spectral_error(fg.time, mean, standard_dev, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error(model, data):
    """Calculate point-wise error between original data and a model fit of that data.

    Parameters
    ----------
    model : 1d array
        The model.
    data : 1d array
        The original data that is being modeled.

    Returns
    -------
    1d array
        Calculated values of the difference between the data and the model.
    """

    return np.abs(model - data)
