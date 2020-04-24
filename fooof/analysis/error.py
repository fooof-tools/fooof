"""Functions to analyze and investigate FOOOF results - model fit error."""

import numpy as np

from fooof.sim.gen import gen_model
from fooof.plts.error import plot_spectral_error
from fooof.core.errors import NoModelError, NoDataError

###################################################################################################
###################################################################################################

def compute_pointwise_error_fm(fm, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the frequency by frequency error of a model fit from a FOOOF object.

    Parameters
    ----------
    fm : FOOOF
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

    errors = compute_pointwise_error(fm.fooofed_spectrum_, fm.power_spectrum)

    if plot_errors:
        plot_spectral_error(fm.freqs, errors, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error_fg(fg, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the frequency by frequency error of model fits from a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup
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

    if not np.any(fg.power_spectra):
        raise NoDataError("Data must be available in the object to calculate errors.")
    if not fg.has_model:
        raise NoModelError("No model is available to use, can not proceed.")

    errors = np.zeros_like(fg.power_spectra)

    for ind, (res, data) in enumerate(zip(fg, fg.power_spectra)):

        model = gen_model(fg.freqs, res.aperiodic_params, res.gaussian_params)
        errors[ind, :] = np.abs(model - data)

    mean = np.mean(errors, 0)
    standard_dev = np.std(errors, 0)

    if plot_errors:
        plot_spectral_error(fg.freqs, mean, standard_dev, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error(model, data):
    """Calculate pointwise error between original data and a model fit of that data.

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
