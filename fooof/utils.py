"""Basic utility functions for FOOOF."""

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
        - It does not round to below or above f_low and f_high, respectively.
    """

    # Create mask to index only requested frequencies
    f_mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])

    # Restrict freqs & psd to requested range
    freqs_ext = freqs[f_mask]
    psd_ext = psd[f_mask]

    return freqs_ext, psd_ext


def mk_freq_vector(freq_range, freq_res):
    """Regenerate a frequency vector, from the frequency range and resolution.

    Parameters
    ----------
    freq_range : list of [float, float]
        Frequency range of desired frequency vector, as [f_low, f_high].
    freq_res : float
        Frequency resolution of desired frequency vector.

    Returns
    -------
    1d array
        Vector of frequency values.
    """

    return np.arange(freq_range[0], freq_range[1]+freq_res, freq_res)


def check_array_dim(arr):
    """Check that parameter array has the correct shape, and reshape if not."""

    return np.empty([0, 3]) if arr.ndim == 1 else arr


def get_attribute_names():
    """Get dictionary specifying FOOOF object names and kind of attributes."""

    attributes = {'results' : ['background_params_', 'oscillation_params_', 'error_', 'r2_',
                               '_gaussian_params', 'freq_range', 'freq_res'],
                  'settings' : ['amp_std_thresh', 'bandwidth_limits', 'bg_use_knee',
                                'max_n_oscs', 'min_amp'],
                  'dat' : ['psd', 'freq_range', 'freq_res'],
                  'hidden_settings' : ['_bg_fit_func', '_std_limits', '_bg_bounds'],
                  'arrays' : ['freqs', 'psd', 'background_params_', 'oscillation_params_',
                              '_gaussian_params']}
    attributes['all_settings'] = attributes['settings'] + attributes['hidden_settings']

    return attributes
