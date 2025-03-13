"""Checker functions."""

from inspect import isgenerator
from itertools import chain, repeat

import numpy as np

###################################################################################################
###################################################################################################

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


def check_inds(inds, length=None):
    """Check various ways to indicate indices and convert to a consistent format.

    Parameters
    ----------
    inds : int or slice or range or array_like of int or array_like of bool or None
        Indices, indicated in multiple possible ways.
        If None, converted to slice object representing all inds.

    Returns
    -------
    array of int or slice or range
        Indices.

    Notes
    -----
    The goal of this function is to convert multiple possible
    ways of indicating a set of indices into one consistent format.
    This function works only on indices defined for 1 dimension.
    """

    # If inds is None, replace with slice object to get all indices
    if inds is None:
        inds = slice(None, None)
    # Typecasting: if a single int, convert to an array
    if isinstance(inds, int):
        inds = np.array([inds])
    # Typecasting: if a list, convert to an array
    if isinstance(inds, (list)):
        inds = np.array(inds)
    # Conversion: if array is boolean, get integer indices of True
    if isinstance(inds, np.ndarray) and inds.dtype == bool:
        inds = np.where(inds)[0]
    # If slice type, check for converting length
    if isinstance(inds, slice):
        if not inds.stop and length:
            inds = range(inds.start if inds.start else 0,
                         length, inds.step if inds.step else 1)

    return inds
