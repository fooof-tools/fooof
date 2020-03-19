"""Test functions for fooof.utils.download."""

import os
import shutil

import numpy as np

from fooof.utils.download import *

###################################################################################################
###################################################################################################

TEST_FOLDER = 'test_data'

def clean_up_downloads():

    shutil.rmtree(TEST_FOLDER)

###################################################################################################
###################################################################################################

def test_check_data_folder():

    check_data_folder(TEST_FOLDER)
    assert os.path.isdir(TEST_FOLDER)

def test_check_data_file():

    filename = 'freqs.npy'

    check_data_file(filename, TEST_FOLDER)
    assert os.path.isfile(os.path.join(TEST_FOLDER, filename))

def test_fetch_fooof_data():

    filename = 'spectrum.npy'

    fetch_fooof_data(filename, folder=TEST_FOLDER)
    assert os.path.isfile(os.path.join(TEST_FOLDER, filename))

    clean_up_downloads()

def test_load_fooof_data():

    filename = 'freqs.npy'

    data = load_fooof_data(filename, folder=TEST_FOLDER)
    assert isinstance(data, np.ndarray)

    clean_up_downloads()
