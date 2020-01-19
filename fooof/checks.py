"""Functions to check FOOOF models."""

import numpy as np

from fooof.sim.gen import gen_model
from fooof.core.info import get_description
from fooof.core.errors import NoModelError, NoDataError
from fooof.utils import compute_pointwise_error
from fooof.plts.spectra import plot_spectrum_error

###################################################################################################
###################################################################################################

def get_info(fooof_obj, aspect):
    """Get a specified selection of information from a FOOOF derived object.

    Parameters
    ----------
    fooof_obj : FOOOF or FOOOFGroup
        Object to get attributes from.
    aspect : {'settings', 'meta_data', 'results'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    dict
        The set of specified info from the FOOOF derived object.
    """

    return {key : getattr(fooof_obj, key) for key in get_description()[aspect]}


def compare_info(fooof_lst, aspect):
    """Compare a specified aspect of FOOOF objects across instances.

    Parameters
    ----------
    fooof_lst : list of FOOOF or list of FOOOFGroup
        Objects whose attributes are to be compared.
    aspect : {'setting', 'meta_data'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    consistent : bool
        Whether the settings are consistent across the input list of objects.
    """

    # Check specified aspect of the objects are the same across instances
    for f_obj_1, f_obj_2 in zip(fooof_lst[:-1], fooof_lst[1:]):
        if getattr(f_obj_1, 'get_' + aspect)() != getattr(f_obj_2, 'get_' + aspect)():
            consistent = False
            break
    else:
        consistent = True

    return consistent


def compute_pointwise_error_fm(fm, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the frequency by frequency error of a model fit from a FOOOF object.

    Parameters
    ----------
    fm : FOOOF
        A FOOOF object containing the data and model.
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
        plot_spectrum_error(fm.freqs, errors, **plt_kwargs)

    if return_errors:
        return errors


def compute_pointwise_error_fg(fg, plot_errors=True, return_errors=False, **plt_kwargs):
    """Calculate the frequency by frequency error of model fits from a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup
        A FOOOFGroup object containing the data and model.
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
        plot_spectrum_error(fg.freqs, mean, standard_dev, **plt_kwargs)

    if return_errors:
        return errors
