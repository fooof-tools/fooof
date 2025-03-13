"""File I/O for specific file types."""

import io
import json
from json import JSONDecodeError

from specparam.io.utils import create_file_path
from specparam.core.items import OBJ_DESC
from specparam.utils.convert import dict_lst_to_array

###################################################################################################
###################################################################################################

def save_json(data, file_name, file_path=None, append=False):
    """Save out to a JSON or JSONlines file.

    Parameters
    ----------
    data : dict
        Data to save out.
    file_name : str or FileObject
        File to save data to.
    file_path : Path or str, optional
        Path to directory to load from. If None, saves to current directory.
    append : bool, optional, default: False
        Whether to append to an existing file, if available.
        This option is only valid (and only used) if 'file_name' is a str.
    """

    if isinstance(file_name, str):

        # Save out, appending to existing file if set to, or not (creates new JSON file)
        full_path = create_file_path(file_name, file_path, 'json')
        with open(full_path, 'a' if append else 'w') as outfile:
            json.dump(data, outfile)
            if append:
                outfile.write('\n')

    # Save out - append to given file object (appends to a JSONlines file)
    elif isinstance(file_name, io.IOBase):
        json.dump(data, file_name)
        file_name.write('\n')

    else:
        raise ValueError("Save file not understood.")


def load_json(file_name, file_path):
    """Load json file.

    Parameters
    ----------
    file_name : str or FileObject
        File to load data from.
    file_path : Path or str
        Path to directory to load from.

    Returns
    -------
    data : dict
        Dictionary of data loaded from file.
    """

    # Load data from file
    if isinstance(file_name, str):
        with open(create_file_path(file_name, file_path, 'json'), 'r') as infile:
            data = json.load(infile)
    elif isinstance(file_name, io.IOBase):
        data = json.loads(file_name.readline())

    # Get dictionary of available attributes, and convert specified lists back into arrays
    data = dict_lst_to_array(data, OBJ_DESC['arrays'])

    return data


def load_jsonlines(file_name, file_path):
    """Load a json-lines file, yielding data line by line.

    Parameters
    ----------
    file_name : str
        File to load data from.
    file_path : Path or str
        Path to directory from load from.

    Yields
    ------
    dict
        Dictionary of data loaded from file.
    """

    with open(create_file_path(file_name, file_path, 'json'), 'r') as f_obj:

        while True:

            # Load each line, as JSON file
            try:
                yield load_json(f_obj, '')

            # Break off when get a JSON error - end of the file
            except JSONDecodeError:
                break
