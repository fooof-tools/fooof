"""Util functions for FOOOF."""

import numpy as np

###################################################################################################
###################################################################################################

def overlap(lst_1, lst_2):
    """Checks if boundary definitions 'a' are entirely within boundary definitions 'b'.

    Parameters
    ----------
    a, b : list of [float, float]
        Boundary definitions.

    Returns
    -------
    bool
        True if a is entirely within the bounds of b, False otherwise.
    """

    return bool((lst_1[0] >= lst_2[0]) and (lst_1[0] <= lst_2[1]) and \
    			(lst_1[1] >= lst_2[0]) and (lst_1[1] <= lst_2[1]))

    # Above should perform the same as explicit if statement, as below:
    #if (lst_1[0] >= lst_2[0]) and (lst_1[0] <= lst_2[1]) and \
    #   (lst_1[1] >= lst_2[0]) and (lst_1[1] <= lst_2[1]):
    #    return True
    #else:
    #    return False


def group_three(vec):
    """Takes array of inputs, groups by three.

	Parameters
	----------
	vec : 1d array
		Array of items to sort by 3 - must be divisible by three.

	Returns
	-------
	list of list

    """

    return [list(vec[i:i+3]) for i in range(0, len(vec), 3)]


def get_index_from_vector(input_vector, element_value):
    """Returns index for input closest to desired element value.

    Parameters
    ----------
    input_vector : 1d array
        Vector of values to search through.
    element_value : float
        Value to search for in input vector.

    Returns
    -------
    idx : int
        Index closest to element value.
    """

    loc = input_vector - element_value
    idx = np.where(np.abs(loc) == np.min(np.abs(loc)))

    return idx[0][0]
