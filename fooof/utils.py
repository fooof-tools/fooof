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

    Notes
    -----
    This function is not symmetrical with respect to inputs.
        overlap(lst_1, lst_2) != overlap(lst_2, lst_1).
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
        List of lists, each with three items.
    """

    if len(vec) % 3 != 0:
        raise ValueError('Wrong size array to group by three.')

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


def trim_psd(input_frequency_vector, input_psd, frequency_range):
    """Extract PSD, and frequency vector, to desired frequency range.

    Parameters
    ----------
    input_frequency_vector :
        Frequency values for the PSD.
    input_psd : 2d array
        Power spectral density values.
    frequency_range : list of [float, float]
        Desired frequency range of PSD.

    Returns
    -------
    output_frequency_vector : 1d array
        Extracted frequency values for the PSD.
    trimmed_psd :
        Extracted power spectral density values.

    NOTEs (TODO):
    This function currently assumes 2d input. Should it?
        In particular, it assumes column vectors of PSDs.
    It also (using get_index_from_vector) round bi-directionally.
        Not obvious, and maybe not desirable.
    It also, also: doesn't include last requested frequency.
        So f_range [2, 30] would include f_vals 2 to one f_val prior to 30.
        With the rounding: this happens
    """

    idx = [get_index_from_vector(input_frequency_vector, freq) for freq in frequency_range]

    output_frequency_vector = input_frequency_vector[idx[0]:idx[1]]
    trimmed_psd = input_psd[idx[0]:idx[1]]#, :]

    return output_frequency_vector, trimmed_psd
