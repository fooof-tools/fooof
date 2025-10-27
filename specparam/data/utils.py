""""Utility functions for working with data and data objects."""

import numpy as np

###################################################################################################
###################################################################################################

def _get_field_ind(modes, component, field):
    """Helper function to get the index for a specified field.

    Parameters
    ----------
    modes : Modes
        Modes description.
    component : {'aperiodic', 'peak'}
        Component label.
    field : str
        Field label.
    """

    # If field specified as string, get mapping back to integer
    if isinstance(field, str):
        if component == 'aperiodic':
            field = modes.aperiodic.params.indices[field.lower()]
        if component  == 'peak':
            field = modes.periodic.params.indices[field.lower()]

    return field


def _get_metric_labels(metrics, category, measure):
    """Get a selected set of metric labels.

    Parameters
    ----------
    metrics : list of str
        List of metric labels.
    category : str or list of str
        Category of metric to extract, e.g. 'error' or 'gof'.
        If 'all', gets all metric labels.
    measure : str or list of str
        Name of the specific measure(s) to extract.
    """

    if category == 'all':
        labels = metrics
    elif category and not measure:
        labels = [label for label in metrics if category in label]
    elif isinstance(measure, list):
        labels = [category + '_' + label for label in measure]
    else:
        labels = [category + '_' + measure]

    return labels


def get_model_params(fit_results, modes, component, field=None, version=None):
    """Return model fit parameters for specified feature(s) from FitResults object.

    Parameters
    ----------
    fit_results : FitResults
        Results of a model fit.
    modes : Modes
        Model modes definition.
    component : {'aperiodic', 'peak'}
        Name of the component to extract.
    field : str or int, optional
        Column name / index to extract from selected data, if requested.
        See `SpectralModel.modes.check_params` for a description of parameter field names.

    Returns
    -------
    out : float or 1d array
        Requested data.
    """

    # TEMP:
    if not version:
        version = 'converted' if component == 'peak' else 'fit'
    component = 'peak' if component == 'periodic' else component

    # Use helper function to sort out name and column selection
    ind = None
    ind = _get_field_ind(modes, component, field)
    component = component + '_' + version

    # Extract the requested data attribute from object
    out = getattr(fit_results, component)

    # Periodic values can be empty arrays and if so, replace with NaN array
    if isinstance(out, np.ndarray) and out.size == 0:
        out = np.array([np.nan] * modes.periodic.n_params)

    # Select out a specific column, if requested
    if ind is not None:

        # Extract column, & if result is a single value in an array, unpack from array
        out = out[ind] if out.ndim == 1 else out[:, ind]
        out = out[0] if isinstance(out, np.ndarray) and out.size == 1 else out

    return out


def get_group_params(group_results, modes, component, field=None, version=None):
    """Extract a specified set of parameters from a set of group results.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects, reflecting model results across a group of power spectra.
    modes : Modes
        Model modes definition.
    component : {'aperiodic', 'peak'}
        Name of the data field to extract across the group.
    field : str or int, optional
        Column name / index to extract from selected data, if requested.
        See `SpectralModel.modes.check_params` for a description of parameter field names.
    version : {'fit', 'converted'}, optional
        TODO

    Returns
    -------
    out : ndarray
        Requested data.
    """

    # TEMP:
    if not version:
        version = 'converted' if component == 'peak' else 'fit'
    component = 'peak' if component == 'periodic' else component

    # Use helper function to sort out name and column selection
    ind = None
    ind = _get_field_ind(modes, component, field)
    component = component + '_' + version

    # Pull out the requested data field from the group data
    # As a special case, peak_params are pulled out in a way that appends
    #  an extra column, indicating which model each peak comes from
    #if name in ('peak_params', 'gaussian_params'):
    if 'peak' in component:

        # Collect peak data, appending the index of the model it comes from
        out = np.vstack([np.insert(getattr(data, component), modes.periodic.n_params, index, axis=1)
                         for index, data in enumerate(group_results)])

        # This updates index to grab selected column, and the last column
        #   This last column is the 'index' column (model object source)
        if ind is not None:
            ind = [ind, -1]
    else:
        out = np.array([getattr(data, component) for data in group_results])

    # Select out a specific column, if requested
    if ind is not None:
        out = out[:, ind]

    return out


def get_group_metrics(group_results, category, measure=None):
    """Extract metrics from a set of group results.

    Parameters
    ----------
    group_results : list of FitResults
        List of FitResults objects, reflecting model results across a group of power spectra.
    category : str or list of str
        Category of metric to extract, e.g. 'error' or 'gof'.
        If 'all', returns all metrics.
    measure : str or list of str, optional
        Name of the specific measure(s) to extract.

    Returns
    -------
    group_metrics : array
        Requested metric(s).
    """

    group_metrics = []
    for label in _get_metric_labels(list(group_results[0].metrics.keys()), category, measure):
        group_metrics.append(np.array([getattr(fres, 'metrics')[label] for fres in group_results]))
    group_metrics = np.squeeze(np.array(group_metrics))

    return group_metrics


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
