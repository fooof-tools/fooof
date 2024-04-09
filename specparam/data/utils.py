""""Utility functions for working with data and data objects."""

import numpy as np

from specparam.core.info import get_indices
from specparam.core.funcs import infer_ap_func

###################################################################################################
###################################################################################################

def get_model_params(fit_results, name, col=None):
    """Return model fit parameters for specified feature(s).

    Parameters
    ----------
    fit_results : FitResults
        Results of a model fit.
    name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
        Name of the data field to extract.
    col : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
        Column name / index to extract from selected data, if requested.
        Only used for name of {'aperiodic_params', 'peak_params', 'gaussian_params'}.

    Returns
    -------
    out : float or 1d array
        Requested data.
    """

    # If col specified as string, get mapping back to integer
    if isinstance(col, str):
        col = get_indices(infer_ap_func(fit_results.aperiodic_params))[col]

    # Allow for shortcut alias, without adding `_params`
    if name in ['aperiodic', 'peak', 'gaussian']:
        name = name + '_params'

    # Extract the requested data field from object
    out = getattr(fit_results, name)

    # Periodic values can be empty arrays and if so, replace with NaN array
    if isinstance(out, np.ndarray) and out.size == 0:
        out = np.array([np.nan, np.nan, np.nan])

    # Select out a specific column, if requested
    if col is not None:

        # Extract column, & if result is a single value in an array, unpack from array
        out = out[col] if out.ndim == 1 else out[:, col]
        out = out[0] if isinstance(out, np.ndarray) and out.size == 1 else out

    return out


def get_group_params(group_results, name, col=None):
    """Extract a specified set of parameters from a set of group results.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects, reflecting model results across a group of power spectra.
    name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
        Name of the data field to extract across the group.
    col : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
        Column name / index to extract from selected data, if requested.
        Only used for name of {'aperiodic_params', 'peak_params', 'gaussian_params'}.

    Returns
    -------
    out : ndarray
        Requested data.
    """

    # Allow for shortcut alias, without adding `_params`
    if name in ['aperiodic', 'peak', 'gaussian']:
        name = name + '_params'

    # If col specified as string, get mapping back to integer
    if isinstance(col, str):
        col = get_indices(infer_ap_func(group_results[0].aperiodic_params))[col]
    elif isinstance(col, int):
        if col not in [0, 1, 2]:
            raise ValueError("Input value for `col` not valid.")

    # Pull out the requested data field from the group data
    # As a special case, peak_params are pulled out in a way that appends
    #  an extra column, indicating which model each peak comes from
    if name in ('peak_params', 'gaussian_params'):

        # Collect peak data, appending the index of the model it comes from
        out = np.vstack([np.insert(getattr(data, name), 3, index, axis=1)
                         for index, data in enumerate(group_results)])

        # This updates index to grab selected column, and the last column
        #   This last column is the 'index' column (model object source)
        if col is not None:
            col = [col, -1]
    else:
        out = np.array([getattr(data, name) for data in group_results])

    # Select out a specific column, if requested
    if col is not None:
        out = out[:, col]

    return out


def get_periodic_labels(results):
    """Get labels of periodic fields from a dictionary representation of parameter results.

    Parameters
    ----------
    results : dict
        A results dictionary with parameter label keys and corresponding parameter values.

    Returns
    -------
    dict
        Dictionary indicating the periodic related labels from the input results.
        Has keys ['cf', 'pw', 'bw'] with corresponding values of related labels in the input.
    """

    keys = list(results.keys())

    outs = {}
    for label in ['cf', 'pw', 'bw']:
        outs[label] = [key for key in keys if label in key]

    return outs


def get_band_labels(indict):
    """Get a list of band labels from

    Parameters
    ----------
    indict : dict
        Dictionary of results and/or labels to get the band labels from.
        Can be wither a `time_results` or `periodic_labels` dictionary.

    Returns
    -------
    band_labels : list of str
        List of band labels.
    """

    # If it's a results dictionary, convert to periodic labels
    if 'offset' in indict:
        indict = get_periodic_labels(indict)

    n_bands = len(indict['cf'])

    band_labels = []
    for ind in range(n_bands):
        tband_label = indict['cf'][ind].split('_')
        tband_label.remove('cf')
        band_labels.append(tband_label[0])

    return band_labels


def get_results_by_ind(results, ind):
    """Get a specified index from a dictionary of results.

    Parameters
    ----------
    results : dict
        A results dictionary with parameter label keys and corresponding parameter values.
    ind : int
        Index to extract from results.

    Returns
    -------
    dict
        Dictionary including the results for the specified index.
    """

    out = {}
    for key in results.keys():
        out[key] = results[key][ind]

    return out


def get_results_by_row(results, ind):
    """Get a specified index from a dictionary of results across events.

    Parameters
    ----------
    results : dict
        A results dictionary with parameter label keys and corresponding parameter values.
    ind : int
        Index to extract from results.

    Returns
    -------
    dict
        Dictionary including the results for the specified index.
    """

    outs = {}
    for key in results.keys():
        outs[key] = results[key][ind, :]

    return outs


def flatten_results_dict(results):
    """Flatten a results dictionary containing results across events.

    Parameters
    ----------
    results : dict
        Results dictionary wherein parameters are organized in 2d arrays as [n_events, n_windows].

    Returns
    -------
    flatdict : dict
        Flattened results dictionary.
    """

    keys = list(results.keys())
    n_events, n_windows = results[keys[0]].shape

    flatdict = {
        'event' : np.repeat(range(n_events), n_windows),
        'window' : np.tile(range(n_windows), n_events),
    }

    for key in keys:
        flatdict[key] = results[key].flatten()

    return flatdict
