"""Internal utility functions for FOOOF."""

import numpy as np

###################################################################################################
###################################################################################################

def get_attribute_names():
    """Get dictionary specifying FOOOF object names and kind of attributes."""

    attributes = {'results' : ['background_params_', 'oscillation_params_', 'error_', 'r2_',
                               '_gaussian_params', 'freq_range', 'freq_res'],
                  'settings' : ['amp_std_thresh', 'bandwidth_limits', 'bg_use_knee',
                                'max_n_oscs', 'min_amp'],
                  'dat' : ['psd', 'freq_range', 'freq_res'],
                  'hidden_settings' : ['_bg_fit_func', '_std_limits', '_bg_bounds'],
                  'arrays' : ['freqs', 'psd', 'background_params_', 'oscillation_params_',
                              '_gaussian_params'],
                  'alias_funcs' : ['plot', 'save', 'create_report']}
    attributes['all_settings'] = attributes['settings'] + attributes['hidden_settings']

    return attributes


def docs_drop_param(ds):
    """Drop the first parameter description for a string representation of a docstring.

    Parameters
    ----------
    ds : str
        Docstring to drop first parameter from.
    """

    tm = '----------\n'
    ind = ds.find(tm) + len(tm)
    fr, ba = ds[:ind], ds[ind:]

    for i in range(2):
        ba = ba[ba.find('\n')+1:]

    return fr + ba


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
    """Check that parameter array has the correct shape, and reshape if not."""

    return np.empty([0, 3]) if arr.ndim == 1 else arr
