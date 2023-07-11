""""Utility functions for working with data and data objects."""

###################################################################################################
###################################################################################################

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
