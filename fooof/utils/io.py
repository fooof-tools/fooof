"""Utilities for input / ouput for data and models."""

import numpy as np

from fooof.objs import FOOOF, FOOOFGroup
from fooof.core.io import load_json, load_jsonlines

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

    # Initialize a FOOOF object
    fm = FOOOF()

    # Load JSON file, add to self and check loaded data
    data = load_json(file_name, file_path)

    # Add data and check loaded settings and results
    fm._add_from_dict(data)
    fm._check_loaded_settings(data)
    fm._check_loaded_results(data)

    # Regenerate model components, based on what is available
    if regenerate:
        if fm.freq_res:
            fm._regenerate_freqs()
        if np.all(fm.freqs) and np.all(fm.aperiodic_params_):
            fm._regenerate_model()

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

    fg = FOOOFGroup()

    power_spectra = []
    for ind, data in enumerate(load_jsonlines(file_name, file_path)):

        fg._add_from_dict(data)

        # Collect power spectra, if present
        if 'power_spectrum' in data.keys():
            power_spectra.append(data['power_spectrum'])

        # Only load settings from first line
        #   All other lines, if there, will be duplicates
        if ind == 0:
            fg._check_loaded_settings(data)

        fg._check_loaded_results(data)
        fg.group_results.append(fg._get_results())

    # Add data, if they were loaded
    if power_spectra:
        fg.power_spectra = np.array(power_spectra)

    # Reset peripheral data from last loaded result, keeping freqs info
    fg._reset_data_results(clear_spectrum=True, clear_results=True)

    return fg
