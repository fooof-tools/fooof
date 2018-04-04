"""Utility functions & decorators for dealing with FOOOF, as a module."""

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
    *args accepts either 1 or 2 strings, as pass through inputs to import_module.
        To import a whole module, pass a single string, ex: ('matplotlib').
        To import a specific package, pass two strings, ex: ('.pyplot', 'matplotlib')
    """

    try:
        mod = import_module(*args)
    except ImportError:
        mod = False

    # Prior to py 3.5.4, import module could throw a SystemError
    #  Older approach requires the parent module be imported first
    #  If triggered, re-check for module after first importing the parent
    except SystemError:
        try:
            _ = import_module(args[-1])
            mod = import_module(*args)
        except ImportError:
            mod = False

    return mod


def get_obj_desc():
    """Get dictionary specifying FOOOF object names and kind of attributes.

    Returns
    -------
    attibutes : dict
        Mapping of FOOOF object attributes, and what kind of data they are.
    """

    attributes = {'results' : ['background_params_', 'peak_params_', 'error_',
                               'r_squared_', '_gaussian_params'],
                  'settings' : ['peak_width_limits', 'max_n_peaks', 'min_peak_amplitude',
                                'peak_threshold', 'background_mode'],
                  'data' : ['power_spectrum', 'freq_range', 'freq_res'],
                  'freq_info' : ['freq_range', 'freq_res'],
                  'arrays' : ['freqs', 'power_spectrum', 'background_params_',
                              'peak_params_', '_gaussian_params']}

    return attributes


def get_data_indices(background_mode):
    """Get a dictionary mapping the column labels to indices in FOOOF data (FOOOFResults).

    Parameters
    ----------
    background_mode : {'fixed', 'knee'}
        Which approach taken to fit the background.

    Returns
    -------
    indices : dict
        Mapping for data columns to the column indices in which they appear.
    """

    indices = {
        'CF'  : 0,
        'Amp' : 1,
        'BW'  : 2,
        'intercept' : 0,
        'knee'      : 1 if background_mode == 'knee' else None,
        'slope'     : 1 if background_mode == 'fixed' else 2
    }

    return indices


def docs_drop_param(docstring):
    """Drop the first parameter description for a string representation of a docstring.

    Parameters
    ----------
    docstring : str
        Docstring to drop first parameter from.

    Returns
    -------
    str
        New docstring, with first parameter dropped.

    Notes
    -----
    - This function assumes numpy docs standards.
    - It also assumes the parameter description to be dropped is only 2 lines long.
    """

    sep = '----------\n'
    ind = docstring.find(sep) + len(sep)
    front, back = docstring[:ind], docstring[ind:]

    for loop in range(2):
        back = back[back.find('\n')+1:]

    return front + back


def docs_append_to_section(docstring, section, add):
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
    str
        Updated docstring.

    Notes
    -----
    - This function assumes numpy docs standards.
    """

    return '\n\n'.join([split + add if section in split else split \
                        for split in docstring.split('\n\n')])


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
    """Check if an optional dependency is available (decorator).

    Parameters
    ----------
    dep : module or False
        Module, if successfully imported, or boolean (False) if not.
    name : str
        Full name of the module, to be printed in message.

    Returns
    -------
    wrap : callable
        The decorated function.
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
