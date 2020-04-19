"""File I/O for FOOOF."""

import io
import os
import json
from json import JSONDecodeError

from fooof.core.items import OBJ_DESC
from fooof.core.utils import dict_array_to_lst, dict_select_keys, dict_lst_to_array

###################################################################################################
###################################################################################################

def fname(file_name, extension):
    """Check a filename, adding an extension if not already specified.

    Parameters
    ----------
    file_name : str
        String that specifies a file name.
    extension : str
        String of the extension (without a period) to be added if one isn't already present.

    Outputs
    -------
    file_name : str
        String that specifies a file name.
    """

    if len(file_name.split('.')) == 1:
        file_name = file_name + '.' + extension

    return file_name


def fpath(file_path, file_name):
    """Build the full file path from file name and directory.

    Parameters
    ----------
    file_path : str or None
        Path to the directory where the file is located.
    file_name : str
        Name of the file.

    Returns
    -------
    full_path : str
        Full file path to the file, including directory, if provided.

    Notes
    -----
    This function is mainly used to deal with the case in which file_path is None.
    """

    if not file_path:
        full_path = file_name
    else:
        full_path = os.path.join(file_path, file_name)

    return full_path


def save_fm(fm, file_name, file_path=None, append=False,
            save_results=False, save_settings=False, save_data=False):
    """Save out data, results and/or settings from a FOOOF object into a JSON file.

    Parameters
    ----------
    fm : FOOOF
        Object to save data from.
    file_name : str or FileObject
        File to save data to.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    append : bool, optional, default: False
        Whether to append to an existing file, if available.
        This option is only valid (and only used) if 'file_name' is a str.
    save_results : bool, optional
        Whether to save out FOOOF model fit results.
    save_settings : bool, optional
        Whether to save out FOOOF settings.
    save_data : bool, optional
        Whether to save out input data.

    Raises
    ------
    ValueError
        If the save file is not understood.
    """

    # Convert object to dictionary & convert all arrays to lists, for JSON serializing
    obj_dict = dict_array_to_lst(fm.__dict__)

    # Set and select which variables to keep. Use a set to drop any potential overlap
    #   Note that results also saves frequency information to be able to recreate freq vector
    keep = set((OBJ_DESC['results'] + OBJ_DESC['meta_data'] if save_results else []) + \
               (OBJ_DESC['settings'] if save_settings else []) + \
               (OBJ_DESC['data'] if save_data else []))
    obj_dict = dict_select_keys(obj_dict, keep)

    # Save out - create new file, (creates a JSON file)
    if isinstance(file_name, str) and not append:
        with open(fpath(file_path, fname(file_name, 'json')), 'w') as outfile:
            json.dump(obj_dict, outfile)

    # Save out - append to file_name (appends to a JSONlines file)
    elif isinstance(file_name, str) and append:
        with open(fpath(file_path, fname(file_name, 'json')), 'a') as outfile:
            json.dump(obj_dict, outfile)
            outfile.write('\n')

    # Save out - append to given file object (appends to a JSONlines file)
    elif isinstance(file_name, io.IOBase):
        json.dump(obj_dict, file_name)
        file_name.write('\n')

    else:
        raise ValueError("Save file not understood.")


def save_fg(fg, file_name, file_path=None, append=False,
            save_results=False, save_settings=False, save_data=False):
    """Save out results and/or settings from FOOOFGroup object. Saves out to a JSON file.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to save data from.
    file_name : str or FileObject
        File to save data to.
    file_path : str, optional
        Path to directory to load from. If None, loads from current directory.
    append : bool, optional, default: False
        Whether to append to an existing file, if available.
        This option is only valid (and only used) if 'file_name' is a str.
    save_results : bool, optional
        Whether to save out FOOOF model fit results.
    save_settings : bool, optional
        Whether to save out FOOOF settings.
    save_data : bool, optional
        Whether to save out power spectra data.

    Raises
    ------
    ValueError
        If the data or save file specified are not understood.
    """

    if not save_results and not save_settings and not save_data:
        raise ValueError("No data specified for saving.")

    # Save to string specified file, do not append
    if isinstance(file_name, str) and not append:
        with open(fpath(file_path, fname(file_name, 'json')), 'w') as f_obj:
            _save_fg(fg, f_obj, save_results, save_settings, save_data)

    # Save to string specified file, appending
    elif isinstance(file_name, str) and append:
        with open(fpath(file_path, fname(file_name, 'json')), 'a') as f_obj:
            _save_fg(fg, f_obj, save_results, save_settings, save_data)

    # Save to file-object specified file
    elif isinstance(file_name, io.IOBase):
        _save_fg(fg, file_name, save_results, save_settings, save_data)

    else:
        raise ValueError("Save file not understood.")


def load_json(file_name, file_path):
    """Load json file.

    Parameters
    ----------
    file_name : str or FileObject
        File to load data from.
    file_path : str
        Path to directory to load from.

    Returns
    -------
    data : dict
        Dictionary of data loaded from file.
    """

    # Load data from file
    if isinstance(file_name, str):
        with open(fpath(file_path, fname(file_name, 'json')), 'r') as infile:
            data = json.load(infile)
    elif isinstance(file_name, io.IOBase):
        data = json.loads(file_name.readline())

    # Get dictionary of available attributes, and convert specified lists back into arrays
    data = dict_lst_to_array(data, OBJ_DESC['arrays'])

    return data


def load_jsonlines(file_name, file_path):
    """Load a jsonlines file, yielding data line by line.

    Parameters
    ----------
    file_name : str
        File to load data from.
    file_path : str
        Path to directory from load from.

    Yields
    ------
    dict
        Dictionary of data loaded from file.
    """

    with open(fpath(file_path, fname(file_name, 'json')), 'r') as f_obj:

        while True:

            # Load each line, as JSON file
            try:
                yield load_json(f_obj, '')

            # Break off when get a JSON error - end of the file
            except JSONDecodeError:
                break


def _save_fg(fg, f_obj, save_results, save_settings, save_data):
    """Helper function for saving FOOOFGroup - saves data given a file object.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to save data from.
    f_obj : FileObject
        File object to save data to.
    save_results : bool
        Whether to save out FOOOF model fit results.
    save_settings : bool
        Whether to save out FOOOF settings.
    save_data : bool
        Whether to save out power spectra data.
    """

    # Since there is a single set of object settings, save them out once, at the top
    if save_settings:
        save_fm(fg, file_name=f_obj, file_path=None, append=False, save_settings=True)

    # For results & data, loop across all data and/or models, and save each out to a new line
    if save_results or save_data:
        for ind in range(len(fg.group_results)):
            fm = fg.get_fooof(ind, regenerate=False)
            save_fm(fm, file_name=f_obj, file_path=None, append=False,
                    save_results=save_results, save_data=save_data)
