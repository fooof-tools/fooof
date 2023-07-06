"""Conversion functions for organizing model results into alternate representations."""

import numpy as np

from fooof import Bands
from fooof.core.funcs import infer_ap_func
from fooof.core.info import get_ap_indices, get_peak_indices
from fooof.core.modutils import safe_import, check_dependency
from fooof.analysis.periodic import get_band_peak

pd = safe_import('pandas')

###################################################################################################
###################################################################################################

def model_to_dict(fit_results, peak_org):
    """Convert model fit results to a dictionary.

    Parameters
    ----------
    fit_results : FOOOFResults
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
            for label, param in zip(get_peak_indices(), get_band_peak(peaks, f_range)):
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
    fit_results : FOOOFResults
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


@check_dependency(pd, 'pandas')
def group_to_dataframe(fit_results, peak_org):
    """Convert a group of model fit results into a dataframe.

    Parameters
    ----------
    fit_results : list of FOOOFResults
        List of FOOOFResults objects.
    peak_org : int or Bands
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    pd.DataFrame
        Model results organized into a dataframe.
    """

    return pd.DataFrame([model_to_dataframe(f_res, peak_org) for f_res in fit_results])
