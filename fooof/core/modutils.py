"""Utility functions for dealing with FOOOF, as a module."""

from importlib import import_module
from functools import wraps

###################################################################################################
###################################################################################################

def safe_import(*args):
    """Import a module, with a safety net for if the module is not available.

    Parameters
    ----------
    *args : str
        Module to import.

    Returns
    -------
    mod : module or False
        Requested module, if successfully imported, otherwise boolean (False).

    Notes
    -----
    *args accepts
    """

    try:
        mod = import_module(*args)
    except ImportError:
        mod = False

    return mod


def get_obj_desc():
    """Get dictionary specifying FOOOF object names and kind of attributes."""

    attributes = {'results' : ['background_params_', 'oscillation_params_', 'error_', 'r2_',
                               '_gaussian_params', 'freq_range', 'freq_res'],
                  'settings' : ['amp_std_thresh', 'bandwidth_limits', 'bg_use_knee',
                                'max_n_gauss', 'min_amp'],
                  'dat' : ['psd', 'freq_range', 'freq_res'],
                  'hidden_settings' : ['_bg_fit_func', '_std_limits', '_bg_bounds'],
                  'arrays' : ['freqs', 'psd', 'background_params_', 'oscillation_params_',
                              '_gaussian_params']}
    attributes['all_settings'] = attributes['settings'] + attributes['hidden_settings']

    return attributes


def docs_drop_param(ds):
    """Drop the first parameter description for a string representation of a docstring.

    Parameters
    ----------
    ds : str
        Docstring to drop first parameter from.

    Notes
    -----
    - This function assumes numpy docs standards.
    - It also assumes the parameter description to be dropped is only 2 lines long.
    """

    tm = '----------\n'
    ind = ds.find(tm) + len(tm)
    fr, ba = ds[:ind], ds[ind:]

    for i in range(2):
        ba = ba[ba.find('\n')+1:]

    return fr + ba


def docs_append_to_section(ds, section, add):
    """Append extra information to a specified section of a docstring.

    Parameters
    ----------
    ds : str
        Docstring to update.
    section : str
        Name of the section within the dostring to add to.
    add : str
        Text to append to specified section of the docstring.

    Returns
    -------
    new_ds : str
        Updated docstring.

    Notes
    -----
    - This function assumes numpy docs standards.
    """

    return '\n\n'.join([split + add if section in split else split for split in ds.split('\n\n')])


def copy_doc_func_to_method(source):
    """Copy method docstring from function, dropping first parameter (decorator).

    Parameters
    ----------
    source : function
        Source function to copy docstring from.

    Returns
    -------
    wrapper : function
        The decorated function, with updated docs.
    """

    def wrapper(func):

        func.__doc__ = docs_drop_param(source.__doc__)

        return func

    return wrapper


def copy_doc_class(source, section=None, att_add=''):
    """Copy method docstring from class, to another class, adding extra info (decorator).

    Parameters
    ----------
    source : cls
        Source class to copy docstring from.

    Returns
    -------
    wrapper : cls
        The decorated class, with updated docs.
    """

    def wrapper(func):

        func.__doc__ = docs_append_to_section(source.__doc__, 'Attributes', att_add)

        return func

    return wrapper


def check_dependency(dep, name):
    """Decorator to check if an optional dependency is available.

    Parameters
    ----------
    dep : module or False
        Module, if successfully imported, or boolean (False) if not.
    name : str
        Full name of the module, to be printed in message.
    """

    def wrap(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if not dep:
                raise ImportError('Optional FOOOF dependency ' + name + \
                                  ' is required for this functionality.')
            func(*args, **kwargs)
        return wrapped_func
    return wrap
