"""Functions and utilities for downloading example data for fooof."""

import os
from urllib.request import urlretrieve

import numpy as np

###################################################################################################
###################################################################################################

DATA_URL = 'https://raw.githubusercontent.com/fooof-tools/fooof/master/data/'

def check_data_folder(folder):
    """Check if a data folder exists, and create if not.

    Parameters
    ----------
    folder : str
        Name of the folder to check and create if missing.
    """

    if folder and not os.path.isdir(folder):
        os.mkdir(folder)


def check_data_file(filename, folder, url=DATA_URL):
    """Check if a data folder exists, and download it if not.

    Parameters
    ----------
    filename : str
        Name of the data file to check and download if missing.
    folder : str
        Name of the folder to save the datafile to.
    """

    filepath = os.path.join(folder, filename)

    if not os.path.isfile(filepath):
        urlretrieve(url + filename, filename=filepath)


def fetch_fooof_data(filename, folder='data', url=DATA_URL):
    """Download a data file for FOOOF.

    Parameters
    ----------
    filename : str
        Name of the data file to download.
    folder : str, optional
        Name of the folder to save the datafile to.
    url : str, optional
        The URL to download the data file from.

    Notes
    -----
    This function checks if the file already exists, and downloads it if not.
    To download the file into the local folder, set folder to an empty string ('').
    """

    check_data_folder(folder)
    check_data_file(filename, folder, url)


def load_fooof_data(filename, folder='data', url=DATA_URL):
    """Download, if not already available, and load an example data file for fooof.

    Parameters
    ----------
    filename : str
        Name of the data file to download.
    folder : str, optional
        Name of the folder to save the datafile to.
    url : str, optional
        The URL to download the data file from.

    Returns
    -------
    data : ndarray
        Loaded data file.

    Notes
    -----
    This function assumes that data files are numpy (npy) files.
    """

    fetch_fooof_data(filename, folder, url)
    data = np.load(os.path.join(folder, filename))

    return data
