"""Utility functions & decorators for dealing with FOOOF, as a module."""

from importlib import import_module
from functools import wraps

###################################################################################################
###################################################################################################

def safe_import(*args):
    """Try to import a module, with a safety net for if the module is not available.

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
    The input, `*args`, can be either 1 or 2 strings, as pass through inputs to import_module:

    - To import a whole module, pass a single string, ex: ('matplotlib').
    - To import a specific package, pass two strings, ex: ('.pyplot', 'matplotlib')
    """

    try:
        mod = import_module(*args)
    except ImportError:
        mod = False

    # Prior to Python 3.5.4, import module could throw a SystemError
    #  Older approach requires the parent module be imported first
    #  If triggered, re-check for module after first importing the parent
    except SystemError:
        try:
            _ = import_module(args[-1])
            mod = import_module(*args)
        except ImportError:
            mod = False

    return mod


def check_dependency(dep, name):
    """Decorator that checks if an optional dependency is available.

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

    Raises
    ------
    ImportError
        If the requested dependency is not available.
    """

    def wrap(func):
        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if not dep:
                raise ImportError("Optional FOOOF dependency " + name + \
                                  " is required for this functionality.")
            return func(*args, **kwargs)
        return wrapped_func
    return wrap


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
    This function assumes numpy docs standards.
    It also assumes the parameter description to be dropped is only 2 lines long.
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
    docstring : str
        Docstring to update.
    section : str
        Name of the section within the docstring to add to.
    add : str
        Text to append to specified section of the docstring.

    Returns
    -------
    str
        Updated docstring.

    Notes
    -----
    This function assumes numpydoc documentation standard.
    """

    return '\n\n'.join([split + add if section in split else split \
                        for split in docstring.split('\n\n')])


def copy_doc_func_to_method(source):
    """Decorator that copies method docstring from function, dropping first parameter.

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


def copy_doc_class(source, section='Attributes', add=''):
    """Decorator that copies method docstring from class, to another class, adding extra info.

    Parameters
    ----------
    source : cls
        Source class to copy docstring from.
    section : str, optional, default: 'Attributes'
        Name of the section within the docstring to add to.
     add : str, optional
        Text to append to specified section of the docstring.

    Returns
    -------
    wrapper : cls
        The decorated class, with updated docs.
    """

    def wrapper(func):

        func.__doc__ = docs_append_to_section(source.__doc__, section, add)

        return func

    return wrapper
