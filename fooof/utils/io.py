"""Utilities for input / ouput for data and models."""

###################################################################################################
###################################################################################################

def load_fooof(file_name, file_path=None, regenerate=True):
    """Load a FOOOF file into a FOOOF object.

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
    fm : FOOOF
        Object with the loaded data.
    """

    # Initialize a FOOOF object (imported locally to avoid circular imports)
    from fooof.objs import FOOOF
    fm = FOOOF()

    # Load data into object
    fm.load(file_name, file_path, regenerate)

    return fm


def load_fooofgroup(file_name, file_path=None):
    """Load data from file into a FOOOFGroup object.

    Parameters
    ----------
    file_name : str
        File to load data data.
    file_path : str, optional
        Path to directory to load from. If None, loads from current directory.

    Returns
    -------
    fg : FOOOFGroup
        Object with the loaded data.
    """

    # Initialize a FOOOFGroup object (imported locally to avoid circular imports)
    from fooof.objs import FOOOFGroup
    fg = FOOOFGroup()

    # Load data into object
    fg.load(file_name, file_path)

    return fg
