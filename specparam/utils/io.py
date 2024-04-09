"""Utilities for input / output for data and models."""

###################################################################################################
###################################################################################################

def load_model(file_name, file_path=None, regenerate=True):
    """Load a model file into a model object.

    Parameters
    ----------
    file_name : str or FileObject
        File to load the data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.
    regenerate : bool, optional, default: True
        Whether to regenerate the model fit from the loaded data, if data is available.

    Returns
    -------
    model : SpectralModel
        Object with the loaded data.
    """

    # Initialize a model object (imported locally to avoid circular imports)
    from specparam.objs import SpectralModel
    model = SpectralModel()

    # Load data into object
    model.load(file_name, file_path, regenerate)

    return model


def load_group_model(file_name, file_path=None):
    """Load a group file into a group model object.

    Parameters
    ----------
    file_name : str
        File to load data data.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.

    Returns
    -------
    group : SpectralGroupModel
        Object with the loaded data.
    """

    # Initialize a group object (imported locally to avoid circular imports)
    from specparam.objs import SpectralGroupModel
    group = SpectralGroupModel()

    # Load data into object
    group.load(file_name, file_path)

    return group


def load_time_model(file_name, file_path=None, peak_org=None):
    """Load a time file into a time model object.


    Parameters
    ----------
    file_name : str
        File to load data data.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.
    peak_org : int or Bands, optional
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    time : SpectralTimeModel
        Object with the loaded data.
    """

    # Initialize a time object (imported locally to avoid circular imports)
    from specparam.objs import SpectralTimeModel
    time = SpectralTimeModel()

    # Load data into object
    time.load(file_name, file_path, peak_org)

    return time


def load_event_model(file_name, file_path=None, peak_org=None):
    """Load an event file into an event model object.

    Parameters
    ----------
    file_name : str
        File to load data data.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.
    peak_org : int or Bands, optional
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    event : SpectralTimeEventModel
        Object with the loaded data.
    """

    # Initialize an event object (imported locally to avoid circular imports)
    from specparam.objs import SpectralTimeEventModel
    event = SpectralTimeEventModel()

    # Load data into object
    event.load(file_name, file_path, peak_org)

    return event
