"""Module level utilities for managing dependencies."""

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
                raise ImportError("Optional dependency " + name + \
                                  " is required for this functionality.")
            return func(*args, **kwargs)
        return wrapped_func
    return wrap
