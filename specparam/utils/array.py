"""Array related utilities."""

import numpy as np

###################################################################################################
###################################################################################################

def normalize(data):
    """Normalize an array of numerical data (to the range of 0-1).

    Parameters
    ----------
    data : ndarray
        Array of data to normalize.

    Returns
    -------
    np.ndarray
        Normalized data.
    """

    return (data - np.min(data)) / (np.max(data) - np.min(data))


def unlog(arr, base=10):
    """Helper function to unlog an array.

    Parameters
    ----------
    arr : ndarray
        Array.
    base : float
        Base of the log to undo.

    Returns
    -------
    ndarray
        Unlogged array.
    """

    return np.power(base, arr)


def compute_arr_desc(data):
    """Compute descriptive measures of an array of data.

    Parameters
    ----------
    data : array
        Array of numeric data.

    Returns
    -------
    min_val : float
        Minimum value of the array.
    max_val : float
        Maximum value of the array.
    mean_val : float
        Mean value of the array.
    """

    min_val = np.nanmin(data)
    max_val = np.nanmax(data)
    mean_val = np.nanmean(data)

    return min_val, max_val, mean_val
