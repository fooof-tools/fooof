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
