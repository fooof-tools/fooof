"""Utilities for input / output for data and models."""

###################################################################################################
###################################################################################################

def load_ERPparam(file_name, file_path=None, regenerate=True):
    """Load a ERPparam file into a ERPparam object.

    Parameters
    ----------
    file_name : str or FileObject
        File to load the data from.
    file_path : str or None, optional
        Path to directory to load from. If None, loads from current directory.
    regenerate : bool, optional, default: True
        Whether to regenerate the model fit from the loaded data, if data is available.

    Returns
    -------
    fm : ERPparam
        Object with the loaded data.
    """

    # Initialize a ERPparam object (imported locally to avoid circular imports)
    from ERPparam.objs import ERPparam
    fm = ERPparam()

    # Load data into object
    fm.load(file_name, file_path, regenerate)

    return fm


def load_ERPparamGroup(file_name, file_path=None):
    """Load data from file into a ERPparamGroup object.

    Parameters
    ----------
    file_name : str
        File to load data data.
    file_path : str, optional
        Path to directory to load from. If None, loads from current directory.

    Returns
    -------
    fg : ERPparamGroup
        Object with the loaded data.
    """

    # Initialize a ERPparamGroup object (imported locally to avoid circular imports)
    from ERPparam.objs import ERPparamGroup
    fg = ERPparamGroup()

    # Load data into object
    fg.load(file_name, file_path)

    return fg
