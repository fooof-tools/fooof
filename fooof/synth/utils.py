"""Utility functions for use in synthesizing power spectra."""

from inspect import isgenerator
from itertools import chain, repeat

###################################################################################################
###################################################################################################

def _check_iter(obj, length):
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


def _check_flat(lst):
    """Check whether a list is flat, and flatten if not.

    Parameters
    ----------
    lst : list or list of lists
        A list object to be checked and potentially flattened.

    Returns
    -------
    list
        A '1D' list, which is a flattened version of the input.

    Notes
    -----
    This function only deals with one level of nesting.
    """

    # Note: flatten if list contains list(s), but skip if list is empty (which is valid)
    if len(lst) != 0 and isinstance(lst[0], list):
        lst = list(chain(*lst))

    return lst
