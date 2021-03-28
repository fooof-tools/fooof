"""Internal utility functions for FOOOF."""

from inspect import isgenerator
from itertools import chain, repeat

import numpy as np

###################################################################################################
###################################################################################################

def group_three(vec):
    """Group an array of values into threes.

    Parameters
    ----------
    vec : list or 1d array
        List or array of items to group by 3. Length of array must be divisible by three.

    Returns
    -------
    array or list of list
        Array or list of lists, each with three items. Output type will match input type.

    Raises
    ------
    ValueError
        If input data cannot be evenly grouped into threes.
    """

    if len(vec) % 3 != 0:
        raise ValueError("Wrong size array to group by three.")

    # Reshape, if an array, as it's faster, otherwise asssume lise
    if isinstance(vec, np.ndarray):
        return np.reshape(vec, (-1, 3))
    else:
        return [list(vec[ii:ii+3]) for ii in range(0, len(vec), 3)]


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

    return np.argmin(np.abs(array-value))


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
    """Check if an array has 2D shape, and replace with an empty 2d array if not.

    Parameters
    ----------
    arr : ndarray
        Array to check.

    Returns
    -------
    2d array
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

    # Flatten if list contains list(s) - but skip if list is empty (which is valid)
    if len(lst) != 0 and isinstance(lst[0], list):
        lst = list(chain(*lst))

    return lst


def check_inds(inds):
    """Check various ways to indicate indices and convert to a consistent format.

    Parameters
    ----------
    inds : int or array_like of int or array_like of bool
        Indices, indicated in multiple possible ways.

    Returns
    -------
    array of int
        Indices, indicated

    Notes
    -----
    The goal of this function is to convert multiple possible
    ways of indicating a set of indices into one consistent format.
    This function works only on indices defined for 1 dimension.
    """

    # Typecasting: if a single int, convert to an array
    if isinstance(inds, int):
        inds = np.array([inds])
    # Typecasting: if a list or range, convert to an array
    elif isinstance(inds, (list, range)):
        inds = np.array(inds)

    # Conversion: if array is boolean, get integer indices of True
    if inds.dtype == bool:
        inds = np.where(inds)[0]

    return inds


def resolve_aliases(kwargs, aliases):
    """Check and resolve to a standard label for any potential aliases.

    Parameters
    ----------
    kwargs : dict
        Dictionary of labels and their values.
    aliases : dict
        Dictionary of label names and their list of aliases.

    Returns
    -------
    out_kwargs : dict
        Dictionary of labels and their values.

    Notes
    -----
    This function checks all labels in `kwargs` for if they are listed within
    the the `aliases` dictionary. If so, it standardizes this label in `kwargs`
    to the standard label, as defined by the keys of `aliases`.
    """

    out_kwargs = {}

    for key, val in kwargs.items():

        for name, alias in aliases.items():
            if key in alias:
                out_kwargs[name] = val
                break
        else:
            out_kwargs[key] = val

    return out_kwargs
