"""File I/O for model objects.

Notes
-----
Model loader function import model objects locally to prevent circular imports.
"""

import io

from specparam.io.files import save_json
from specparam.io.utils import create_file_path
from specparam.core.items import OBJ_DESC
from specparam.utils.select import dict_select_keys
from specparam.utils.convert import dict_array_to_lst

###################################################################################################
###################################################################################################

def save_model(model, file_name, file_path=None, append=False,
               save_results=False, save_settings=False, save_data=False):
    """Save out data, results and/or settings from a model object into a JSON file.

    Parameters
    ----------
    model : SpectralModel
        Object to save data from.
    file_name : str or FileObject
        File to save data to.
    file_path : Path or str, optional
        Path to directory to save to. If None, saves to current directory.
    append : bool, optional, default: False
        Whether to append to an existing file, if available.
        This option is only valid (and only used) if 'file_name' is a str.
    save_results : bool, optional
        Whether to save out model fit results.
    save_settings : bool, optional
        Whether to save out settings.
    save_data : bool, optional
        Whether to save out input data.

    Raises
    ------
    ValueError
        If the save file is not understood.
    """

    # Convert object to dictionary & convert all arrays to lists, for JSON serializing
    obj_dict = dict_array_to_lst(model.__dict__)

    # Set and select which variables to keep. Use a set to drop any potential overlap
    #   Note that results also saves frequency information to be able to recreate freq vector
    keep = set((OBJ_DESC['results'] + OBJ_DESC['meta_data'] if save_results else []) + \
               (OBJ_DESC['settings'] if save_settings else []) + \
               (OBJ_DESC['data'] if save_data else []))
    obj_dict = dict_select_keys(obj_dict, keep)

    # Save out to json file
    save_json(obj_dict, file_name, file_path, append)


def save_group(group, file_name, file_path=None, append=False,
               save_results=False, save_settings=False, save_data=False):
    """Save out results and/or settings from group object. Saves out to a JSON file.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to save data from.
    file_name : str or FileObject
        File to save data to.
    file_path : Path or str, optional
        Path to directory to load from. If None, saves to current directory.
    append : bool, optional, default: False
        Whether to append to an existing file, if available.
        This option is only valid (and only used) if 'file_name' is a str.
    save_results : bool, optional
        Whether to save out model fit results.
    save_settings : bool, optional
        Whether to save out settings.
    save_data : bool, optional
        Whether to save out power spectra data.

    Raises
    ------
    ValueError
        If the data or save file specified are not understood.
    """

    if not save_results and not save_settings and not save_data:
        raise ValueError("No data specified for saving.")

    # Save to string specified file, specifying whether to append or not
    if isinstance(file_name, str):
        full_path = create_file_path(file_name, file_path, 'json')
        with open(full_path, 'a' if append else 'w') as f_obj:
            _save_group(group, f_obj, save_results, save_settings, save_data)

    # Save to file-object specified file
    elif isinstance(file_name, io.IOBase):
        _save_group(group, file_name, save_results, save_settings, save_data)

    else:
        raise ValueError("Save file not understood.")


def save_event(event, file_name, file_path=None, append=False,
               save_results=False, save_settings=False, save_data=False):
    """Save out results and/or settings from event object. Saves out to a JSON file.

    Parameters
    ----------
    event : SpectralTimeEventModel
        Object to save data from.
    file_name : str or FileObject
        File to save data to.
    file_path : str, optional
        Path to directory to load from. If None, saves to current directory.
    append : bool, optional, default: False
        Whether to append to an existing file, if available.
        This option is only valid (and only used) if 'file_name' is a str.
    save_results : bool, optional
        Whether to save out model fit results.
    save_settings : bool, optional
        Whether to save out settings.
    save_data : bool, optional
        Whether to save out power spectra data.

    Raises
    ------
    ValueError
        If the data or save file specified are not understood.
    """

    fg = event.get_group(None, None, 'group')
    if save_settings and not save_results and not save_data:
        fg.save(file_name, file_path, append=append, save_settings=True)
    else:
        ndigits = len(str(len(event)))
        for ind, gres in enumerate(event.event_group_results):
            fg.group_results = gres
            if save_data:
                fg.power_spectra = event.spectrograms[ind, :, :].T
            fg.save(file_name + '_{:0{ndigits}d}'.format(ind, ndigits=ndigits),
                    file_path=file_path, append=append, save_results=save_results,
                    save_settings=save_settings, save_data=save_data)


def load_model(file_name, file_path=None, regenerate=True):
    """Load a SpectralModel object from file.

    Parameters
    ----------
    file_name : str
        File to load the data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.
    regenerate : bool, optional, default: True
        Whether to regenerate the model fit from the loaded data, if data is available.

    Returns
    -------
    model : SpectralModel
        Loaded model object with data from file.
    """

    from specparam.objs import SpectralModel
    model = SpectralModel()
    model.load(file_name, file_path, regenerate)

    return model


def load_group(file_name, file_path=None):
    """Load a SpectralGroupModel object from file.

    Parameters
    ----------
    file_name : str
        File(s) to load data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.

    Returns
    -------
    group : SpectralGroupModel
        Loaded model object with data from file.
    """

    from specparam.objs import SpectralGroupModel
    group = SpectralGroupModel()
    group.load(file_name, file_path)

    return group


def load_time(file_name, file_path=None, peak_org=None):
    """Load a SpectralTimeModel object from file.

    Parameters
    ----------
    file_name : str
        File(s) to load data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.
    peak_org : int or Bands, optional
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    time : SpectralTimeModel
        Loaded model object with data from file.
    """

    from specparam.objs import SpectralTimeModel
    time = SpectralTimeModel()
    time.load(file_name, file_path, peak_org)

    return time


def load_event(file_name, file_path=None, peak_org=None, event=None):
    """Load a SpectralTimeEventModel object from file.

    Parameters
    ----------
    file_name : str
        File(s) to load data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.
    peak_org : int or Bands, optional
        How to organize peaks.
        If int, extracts the first n peaks.
        If Bands, extracts peaks based on band definitions.

    Returns
    -------
    event : SpectralTimeEventModel
        Loaded model object with data from file.
    """

    from specparam.objs import SpectralTimeEventModel
    event = SpectralTimeEventModel()
    event.load(file_name, file_path, peak_org)

    return event


def _save_group(group, f_obj, save_results, save_settings, save_data):
    """Helper function for saving a group object - saves data given a file object.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to save data from.
    f_obj : FileObject
        File object to save data to.
    save_results : bool
        Whether to save out model fit results.
    save_settings : bool
        Whether to save out settings.
    save_data : bool
        Whether to save out power spectra data.
    """

    # Since there is a single set of object settings, save them out once, at the top
    if save_settings:
        save_model(group, file_name=f_obj, file_path=None, append=False, save_settings=True)

    # For results & data, loop across all data and/or models, and save each out to a new line
    if save_results or save_data:
        for ind in range(len(group.group_results)):
            model = group.get_model(ind, regenerate=False)
            save_model(model, file_name=f_obj, file_path=None, append=False,
                       save_results=save_results, save_data=save_data)
