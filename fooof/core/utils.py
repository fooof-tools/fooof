"""Internal utility functions for FOOOF."""

from inspect import isgenerator
from itertools import chain, repeat

import numpy as np

###################################################################################################
###################################################################################################

def group_three(vec):
    """Takes array of inputs, groups by three.

    Parameters
    ----------
    vec : 1d array
        Array of items to sort by 3 - must be divisible by three.

    Returns
    -------
    list of list
        List of lists, each with three items.
    """

    if len(vec) % 3 != 0:
        raise ValueError('Wrong size array to group by three.')

    return [list(vec[i:i+3]) for i in range(0, len(vec), 3)]


def dict_array_to_lst(in_dict):
    """Convert any numpy arrays present in a dictionary to be lists.

    Parameters
    ----------
    in_dict : dict
        Input dictionary.

    Returns
    -------
    dict
        Output dictionary with all arrays converted to lists.
    """

    return {ke: va.tolist() if isinstance(va, np.ndarray) else va for ke, va in in_dict.items()}


def dict_lst_to_array(in_dict, mk_array):
    """Convert specified lists in a dictionary to be arrays.

    Parameters
    ----------
    in_dict : dict
        Input dictionary.
    mk_array : list of str
        Keys to convert to arrays in the dictionary.

    Returns
    -------
    dict
        Output dictionary with specified lists converted to arrays.
    """

    return {ke: np.array(va) if ke in mk_array else va for ke, va in in_dict.items()}


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


def check_array_dim(arr):
    """Check that parameter array has 2D shape, and reshape if not.

    Parameters
    ----------
    arr : np.array
        Array to check.

    Returns
    -------
    np.array
        Original array, if 2D, or 2D empty array.
    """

    return np.empty([0, 3]) if arr.ndim == 1 else arr


def check_iter(obj, length):
    """Check an object to ensure that it is iterable, and make it iterable if not.

    Parameters
    ----------
    obj : generator or list or float
        Object to check status of.
    length : int
        The (minimum) length the iterator needs to be.

    Returns
    -------
    obj : generator
        Iterable object.
    """

    # If object is not a generator, update to become one
    #   Otherwise (if the object already is a generator) then it gets left as it is
    if not isgenerator(obj):

        if isinstance(obj, list):

            # Check if it's an empty list, if so make it a repeat generator of empty lists
            if len(obj) == 0:
                obj = repeat(obj)

            # If obj is a list of lists of the right length, then we will leave it as is:
            #   as a list of list that will iterate through each element
            # If it is not, then it's turned into a repeat generator
            # Note: checks that it's a list to not have an implicit error
            #   when it's a list of numbers, that happens to be same length as n_spectra
            elif not (isinstance(obj[0], list) and len(obj) == length):
                obj = repeat(obj)

        # If it's not a list, make it a repeat object (repeat int/float)
        else:
            obj = repeat(obj)

    return obj


def check_flat(lst):
    """Check whether a list is flat, and flatten if not.

    Parameters
    ----------
    lst : list or list of lists
        A list object to be checked and potentially flattened.

    Returns
    -------
    lst: list
        A flat (1d) list, which is a flattened version of the input.

    Notes
    -----
    This function only deals with one level of nesting.
    """

    # Note: flatten if list contains list(s), but skip if list is empty (which is valid)
    if len(lst) != 0 and isinstance(lst[0], list):
        lst = list(chain(*lst))

    return lst
