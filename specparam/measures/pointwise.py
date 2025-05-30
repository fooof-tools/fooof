"""Functions to analyze and investigate model fit results, in terms of model fit error."""

import numpy as np

from specparam.sim.gen import gen_model
from specparam.plts.error import plot_spectral_error
from specparam.modutils.errors import NoModelError, NoDataError

###################################################################################################
###################################################################################################

def compute_pointwise_error(model, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the frequency by frequency error of a model fit.

    Parameters
    ----------
    model : SpectralModel
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

    if not model.data.has_data:
        raise NoDataError("Data must be available in the object to calculate errors.")
    if not model.results.has_model:
        raise NoModelError("No model is available to use, can not proceed.")

    errors = compute_pointwise_error_arr(\
        model.results.modeled_spectrum_, model.data.power_spectrum)

    if plot_errors:
        plot_spectral_error(model.data.freqs, errors, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error_group(group, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the frequency by frequency error of model fits for a group of fits.

    Parameters
    ----------
    group : SpectralGroupModel
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

    if not group.data.has_data:
        raise NoDataError("Data must be available in the object to calculate errors.")
    if not group.results.has_model:
        raise NoModelError("No model is available to use, can not proceed.")

    errors = np.zeros_like(group.data.power_spectra)

    for ind, (res, data) in enumerate(zip(group.results, group.data.power_spectra)):

        model = gen_model(group.data.freqs, group.modes.aperiodic, res.aperiodic_params,
                          group.modes.periodic, res.gaussian_params)
        errors[ind, :] = np.abs(model - data)

    mean = np.mean(errors, 0)
    standard_dev = np.std(errors, 0)

    if plot_errors:
        plot_spectral_error(group.data.freqs, mean, standard_dev, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error_arr(model, data):
    """Calculate point-wise error between original data and a model fit of that data.

    Parameters
    ----------
    model : 1d array
        The model of the data.
    data : 1d array
        The original data that is being modeled.

    Returns
    -------
    1d array
        Calculated values of the difference between the data and the model.
    """

    return np.abs(model - data)
