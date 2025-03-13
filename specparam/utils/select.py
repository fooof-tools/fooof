"""Utility functions to select from and/or organize data objects."""

import numpy as np

###################################################################################################
###################################################################################################

def groupby(vec, num):
    """Group an array of values by a specified number.

    Parameters
    ----------
    vec : list or 1d array
        List or array of items to group. Length must be divisible by `num`.
    num : int
        Number to group by.

    Returns
    -------
    array or list of list
        Array or list of lists, each with `num` items. Output type will match input type.

    Raises
    ------
    ValueError
        If input data cannot be evenly grouped into specified number.
    """

    if len(vec) % num != 0:
        raise ValueError("Wrong size array to group by specified number.")

    # Reshape, if an array, as it's faster, otherwise assume list
    if isinstance(vec, np.ndarray):
        return np.reshape(vec, (-1, num))
    else:
        return [list(vec[ii:ii+num]) for ii in range(0, len(vec), num)]


def nearest_ind(array, value):
    """Find the nearest index, in an array, to a given value.

    Parameters
    ----------
    array : 1d array
        An array of values to search within.
    value : float
        The value to find the closest element to.

    Returns
    -------
    int
        Index that is closest to value, for the given array.
    """

    return np.argmin(np.abs(array - value))


# def get_freq_ind(freqs, freq):
#     """Get the index of the  closest frequency value to a specified input frequency.

#     Parameters
#     ----------
#     freqs : 1d array
#         Frequency values.
#     freq : float
#         Frequency value to select closest index to.

#     Returns
#     -------
#     int
#         Index of closest value in `freqs` to `freq`.
#     """

#     return np.argmin(np.abs(freqs - freq))


def dict_select_keys(in_dict, keep):
    """Restrict a dictionary to only keep specified keys.

    Parameters
    ----------
    in_dict : dict
        Input dictionary.
    keep : list or set
        Keys to retain in the dictionary.

    Returns
    -------
    dict
        Output dictionary containing only keys specified in keep.
    """

    return {ke:va for ke, va in in_dict.items() if ke in keep}
