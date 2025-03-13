"""Utilities for working with functions, inlcuding input / outputs."""

###################################################################################################
###################################################################################################

def resolve_aliases(kwargs, aliases):
    """Check and resolve to a standard label for any potential aliases.

    Parameters
    ----------
    kwargs : dict
        Dictionary of labels and their values.
    aliases : dict
        Dictionary of label names and their list of aliases.

    Returns
    -------
    out_kwargs : dict
        Dictionary of labels and their values.

    Notes
    -----
    This function checks all labels in `kwargs` for if they are listed within
    the the `aliases` dictionary. If so, it standardizes this label in `kwargs`
    to the standard label, as defined by the keys of `aliases`.
    """

    out_kwargs = {}

    for key, val in kwargs.items():

        for name, alias in aliases.items():
            if key in alias:
                out_kwargs[name] = val
                break
        else:
            out_kwargs[key] = val

    return out_kwargs
