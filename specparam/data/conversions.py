"""Conversion functions for organizing model results into alternate representations."""

import numpy as np

from specparam import Bands
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.data.periodic import get_band_peak_arr
from specparam.data.utils import flatten_results_dict

pd = safe_import('pandas')

###################################################################################################
###################################################################################################

def model_to_dict(fit_results, modes, bands):
    """Convert model fit results to a dictionary.

    Parameters
    ----------
    fit_results : FitResults
        Results of a model fit.
    modes : Modes
        Model modes definition.
    bands : Bands or int
        How to organize peaks, based on band definitions (Bands) or number of peaks (int).

    Returns
    -------
    dict
        Model results organized into a dictionary.
    """

    fr_dict = {}

    # aperiodic parameters
    for label, param in zip(modes.aperiodic.params.indices, fit_results.aperiodic_params):
        fr_dict[label] = param

    # periodic parameters
    peaks = fit_results.peak_params

    if isinstance(bands, int):

        if len(peaks) < bands:
            nans = [np.array([np.nan] * 3) for ind in range(bands-len(peaks))]
            peaks = np.vstack((peaks, nans))

        for ind, peak in enumerate(peaks[:bands, :]):
            for pe_label, pe_param in zip(modes.periodic.params.indices, peak):
                fr_dict[pe_label + '_' + str(ind)] = pe_param

    elif isinstance(bands, Bands):
        for band, f_range in bands:
            for label, param in zip(modes.periodic.params.indices, get_band_peak_arr(peaks, f_range)):
                fr_dict[band + '_' + label] = param

    # metrics
    for key in fit_results._fields:
        if 'error' in key or 'gof' in key:
            fr_dict[key] = getattr(fit_results, key)

    return fr_dict


@check_dependency(pd, 'pandas')
def model_to_dataframe(fit_results, modes, bands):
    """Convert model fit results to a dataframe.

    Parameters
    ----------
    fit_results : FitResults
        Results of a model fit.
    modes : Modes
        Model modes definition.
    bands : Bands or int
        How to organize peaks, based on band definitions (Bands) or number of peaks (int).

    Returns
    -------
    pd.Series
        Model results organized into a dataframe.
    """

    return pd.Series(model_to_dict(fit_results, modes, bands))


def group_to_dict(group_results, modes, bands):
    """Convert a group of model fit results into a dictionary.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects, reflecting model results across a group of power spectra.
    modes : Modes
        Model modes definition.
    bands : Bands or int
        How to organize peaks, based on band definitions (Bands) or number of peaks (int).

    Returns
    -------
    dict
        Model results organized into a dictionary.
    """

    nres = len(group_results)
    fr_dict = {ke : np.zeros(nres) for ke in model_to_dict(group_results[0], modes, bands)}
    for ind, f_res in enumerate(group_results):
        for key, val in model_to_dict(f_res, modes, bands).items():
            fr_dict[key][ind] = val

    return fr_dict


@check_dependency(pd, 'pandas')
def group_to_dataframe(group_results, modes, bands):
    """Convert a group of model fit results into a dataframe.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects.
    modes : Modes
        Model modes definition.
    bands : Bands or int
        How to organize peaks, based on band definitions (Bands) or number of peaks (int).

    Returns
    -------
    pd.DataFrame
        Model results organized into a dataframe.
    """

    return pd.DataFrame(group_to_dict(group_results, modes, bands))


def event_group_to_dict(event_group_results, modes, bands):
    """Convert the event results to be organized across across and time windows.

    Parameters
    ----------
    event_group_results : list of list of FitResults
        Model fit results from across a set of events.
    modes : Modes
        Model modes definition.
    bands : Bands or int
        How to organize peaks, based on band definitions (Bands) or number of peaks (int).

    Returns
    -------
    event_time_results : dict
        Results dictionary wherein parameters are organized in 2d arrays as [n_events, n_windows].
    """

    event_time_results = {}

    for key in group_to_dict(event_group_results[0], modes, bands):
        event_time_results[key] = []

    for gres in event_group_results:
        dictres = group_to_dict(gres, modes, bands)
        for key, val in dictres.items():
            event_time_results[key].append(val)

    for key in event_time_results:
        event_time_results[key] = np.array(event_time_results[key])

    return event_time_results


@check_dependency(pd, 'pandas')
def event_group_to_dataframe(event_group_results, modes, bands):
    """Convert a group of model fit results into a dataframe.

    Parameters
    ----------
    event_group_results : list of FitResults
        List of FitResults objects.
    modes : Modes
        Model modes definition.
    bands : Bands or int
        How to organize peaks, based on band definitions (Bands) or number of peaks (int).

    Returns
    -------
    pd.DataFrame
        Model results organized into a dataframe.
    """

    return pd.DataFrame(flatten_results_dict(\
        event_group_to_dict(event_group_results, modes, bands)))


@check_dependency(pd, 'pandas')
def dict_to_df(results):
    """Convert a dictionary of model fit results into a dataframe.

    Parameters
    ----------
    results : dict
        Fit results that have already been organized into a flat dictionary.

    Returns
    -------
    pd.DataFrame
        Model results organized into a dataframe.
    """

    return pd.DataFrame(results)
