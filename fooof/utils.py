"""Util functions for FOOOF."""

import numpy as np

###################################################################################################
###################################################################################################

def overlap(lst_1, lst_2):
    """Checks if boundary definitions 'a' are entirely within boundary definitions 'b'.

    Parameters
    ----------
    lst_1, lst_2 : list of [float, float]
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


def trim_psd(freqs, psd, f_range):
    """Extract frequency range of interest from PSD data.

    Parameters
    ----------
    freqs : 1d array
        Frequency values for the PSD.
    psd : 1d array
        Power spectral density values.
    f_range: list of [float, float]
        Frequency range to restrict to.

    Returns
    -------
    freqs_ext : 1d array
        Extracted power spectral density values.
    psd_ext : 1d array
        Extracted frequency values for the PSD.

    Notes
    -----
    This function extracts frequency ranges >= f_low and <= f_high.
        - It does not round to below or above f_low & f_high, respectively.
    """

    # Create mask to index only requested frequencies
    f_mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])

    # Restrict freqs & psd to requested range
    freqs_ext = freqs[f_mask]
    psd_ext = psd[f_mask]

    return freqs_ext, psd_ext
