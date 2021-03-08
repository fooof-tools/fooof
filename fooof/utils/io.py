"""Utilities for input / output for data and models."""

###################################################################################################
###################################################################################################

def load_fooof(file_name, regenerate=True):
    """Load a FOOOF file into a FOOOF object.

    Parameters
    ----------
    file_name : str or FileObject
        File to load the data from, including absolute or relative path.
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
    fm.load(file_name, regenerate)

    return fm


def load_fooofgroup(file_name):
    """Load data from file into a FOOOFGroup object.

    Parameters
    ----------
    file_name : str
        File to load data data, including absolute or relative path.

    Returns
    -------
    fg : FOOOFGroup
        Object with the loaded data.
    """

    # Initialize a FOOOFGroup object (imported locally to avoid circular imports)
    from fooof.objs import FOOOFGroup
    fg = FOOOFGroup()

    # Load data into object
    fg.load(file_name)

    return fg
