"""File I/O for model objects.

Notes
-----
Model loader function import model objects locally to prevent circular imports.
"""

import io

from specparam.io.files import save_json
from specparam.io.utils import create_file_path
from specparam.utils.select import dict_select_keys
from specparam.utils.convert import dict_array_to_lst
from specparam.modutils.docs import (docs_get_section, replace_docstring_sections,
                                     docs_replace_param)

###################################################################################################
###################################################################################################

def save_model(model, file_name, file_path=None, append=False,
               save_results=False, save_settings=False, save_data=False, save_base=None):
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
    save_base : bool, optional
        Whether to save out base data.
        Can be set to False to remove redundant information when saving from multiple models.

    Raises
    ------
    ValueError
        If the save file is not understood.
    """

    # 'Flatten' the model object by extracting relevant attributes to a dictionary
    obj_dict = {**model.data.__dict__, **model.algorithm.settings.values}

    # Convert modes object to their saveable string name
    obj_dict['aperiodic_mode'] = model.modes.aperiodic.name
    obj_dict['periodic_mode'] = model.modes.periodic.name
    mode_labels = ['aperiodic_mode', 'periodic_mode']

    # Add bands information to saveable information
    obj_dict['bands'] = dict(model.results.bands.bands) \
        if not model.results.bands._n_bands else model.results.bands._n_bands
    bands_label = ['bands'] if model.results.bands else []

    # Add parameter results to information to saveable information
    res_dict = model.results.params.asdict()
    obj_dict = {**obj_dict, **res_dict}
    results_labels = list(res_dict.keys())

    # Add metrics to information to saveable information
    obj_dict['metrics'] = model.results.metrics.results

    # Convert all arrays to list for JSON serialization
    obj_dict = dict_array_to_lst(obj_dict)

    # Check for saving out base information / check if base only
    if save_base is None:
        save_base = save_results or save_data
    base_only = (not save_settings and not save_results and not save_data)

    # Set and select which variables to keep. Use a set to drop any potential overlap
    #   Note that results also saves frequency information to be able to recreate freq vector
    keep = set(\
        (mode_labels + bands_label if save_base else []) + \
        (model.data._meta_fields if save_base or base_only else []) + \
        (results_labels + ['metrics'] if save_results else []) + \
        (model.algorithm.settings.names if save_settings else []) + \
        (model.data._fields if save_data else []))

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


@replace_docstring_sections(\
    docs_replace_param(docs_get_section(\
        save_group.__doc__, 'Parameters'),
        'group', 'time : SpectralTimeModel\n        Object to save data from.'))
def save_time(time, file_name, file_path=None, append=False,
              save_results=False, save_settings=False, save_data=False):
    """Save out results and/or settings from time object. Saves out to a JSON file.

    Parameters
    ----------
    % copied in from save_group function.
    """

    save_group(time, file_name, file_path, append,
               save_results, save_settings, save_data)


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
        fg.save(file_name, file_path, append=append, save_settings=save_settings)
    else:
        ndigits = len(str(len(event.results)))
        for ind, gres in enumerate(event.results.event_group_results):
            fg.results.group_results = gres
            if save_data:
                fg.data.power_spectra = event.data.spectrograms[ind, :, :].T
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

    from specparam import SpectralModel
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

    from specparam import SpectralGroupModel
    group = SpectralGroupModel()
    group.load(file_name, file_path)

    return group


def load_time(file_name, file_path=None):
    """Load a SpectralTimeModel object from file.

    Parameters
    ----------
    file_name : str
        File(s) to load data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.

    Returns
    -------
    time : SpectralTimeModel
        Loaded model object with data from file.
    """

    from specparam import SpectralTimeModel
    time = SpectralTimeModel()
    time.load(file_name, file_path)

    return time


def load_event(file_name, file_path=None):
    """Load a SpectralTimeEventModel object from file.

    Parameters
    ----------
    file_name : str
        File(s) to load data from.
    file_path : Path or str, optional
        Path to directory to load from. If None, loads from current directory.

    Returns
    -------
    event : SpectralTimeEventModel
        Loaded model object with data from file.
    """

    from specparam import SpectralTimeEventModel
    event = SpectralTimeEventModel()
    event.load(file_name, file_path)

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
        save_model(group, file_name=f_obj, file_path=None, append=False,
                   save_settings=save_settings, save_base=save_results or save_data)
    else:
        save_model(group, file_name=f_obj, file_path=None, append=False, save_base=True)

    # For results & data, loop across all data and/or models, and save each out to a new line
    if save_results or save_data:
        for ind in range(len(group.results.group_results)):
            model = group.get_model(ind, regenerate=False)
            save_model(model, file_name=f_obj, file_path=None, append=False,
                       save_results=save_results, save_data=save_data, save_base=False)
