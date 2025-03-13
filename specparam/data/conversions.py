"""Conversion functions for organizing model results into alternate representations."""

import numpy as np

from specparam import Bands
from specparam.core.funcs import infer_ap_func
from specparam.core.info import get_ap_indices, get_peak_indices
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.data.periodic import get_band_peak_arr
from specparam.data.utils import flatten_results_dict

pd = safe_import('pandas')

###################################################################################################
###################################################################################################

def model_to_dict(fit_results, peak_org):
    """Convert model fit results to a dictionary.

    Parameters
    ----------
    fit_results : FitResults
        Results of a model fit.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    dict
        Model results organized into a dictionary.
    """

    fr_dict = {}

    # aperiodic parameters
    for label, param in zip(get_ap_indices(infer_ap_func(fit_results.aperiodic_params)),
                            fit_results.aperiodic_params):
        fr_dict[label] = param

    # periodic parameters
    peaks = fit_results.peak_params

    if isinstance(peak_org, int):

        if len(peaks) < peak_org:
            nans = [np.array([np.nan] * 3) for ind in range(peak_org-len(peaks))]
            peaks = np.vstack((peaks, nans))

        for ind, peak in enumerate(peaks[:peak_org, :]):
            for pe_label, pe_param in zip(get_peak_indices(), peak):
                fr_dict[pe_label.lower() + '_' + str(ind)] = pe_param

    elif isinstance(peak_org, Bands):
        for band, f_range in peak_org:
            for label, param in zip(get_peak_indices(), get_band_peak_arr(peaks, f_range)):
                fr_dict[band + '_' + label.lower()] = param

    # goodness-of-fit metrics
    fr_dict['error'] = fit_results.error
    fr_dict['r_squared'] = fit_results.r_squared

    return fr_dict


@check_dependency(pd, 'pandas')
def model_to_dataframe(fit_results, peak_org):
    """Convert model fit results to a dataframe.

    Parameters
    ----------
    fit_results : FitResults
        Results of a model fit.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    pd.Series
        Model results organized into a dataframe.
    """

    return pd.Series(model_to_dict(fit_results, peak_org))


def group_to_dict(group_results, peak_org):
    """Convert a group of model fit results into a dictionary.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects, reflecting model results across a group of power spectra.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    dict
        Model results organized into a dictionary.
    """

    nres = len(group_results)
    fr_dict = {ke : np.zeros(nres) for ke in model_to_dict(group_results[0], peak_org)}
    for ind, f_res in enumerate(group_results):
        for key, val in model_to_dict(f_res, peak_org).items():
            fr_dict[key][ind] = val

    return fr_dict


@check_dependency(pd, 'pandas')
def group_to_dataframe(group_results, peak_org):
    """Convert a group of model fit results into a dataframe.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    pd.DataFrame
        Model results organized into a dataframe.
    """

    return pd.DataFrame(group_to_dict(group_results, peak_org))


def event_group_to_dict(event_group_results, peak_org):
    """Convert the event results to be organized across across and time windows.

    Parameters
    ----------
    event_group_results : list of list of FitResults
        Model fit results from across a set of events.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    event_time_results : dict
        Results dictionary wherein parameters are organized in 2d arrays as [n_events, n_windows].
    """

    event_time_results = {}

    for key in group_to_dict(event_group_results[0], peak_org):
        event_time_results[key] = []

    for gres in event_group_results:
        dictres = group_to_dict(gres, peak_org)
        for key, val in dictres.items():
            event_time_results[key].append(val)

    for key in event_time_results:
        event_time_results[key] = np.array(event_time_results[key])

    return event_time_results


@check_dependency(pd, 'pandas')
def event_group_to_dataframe(event_group_results, peak_org):
    """Convert a group of model fit results into a dataframe.

    Parameters
    ----------
    event_group_results : list of FitResults
        List of FitResults objects.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    pd.DataFrame
        Model results organized into a dataframe.
    """

    return pd.DataFrame(flatten_results_dict(event_group_to_dict(event_group_results, peak_org)))


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
