"""Configuration file for pytest."""

import os
import shutil
import pkg_resources as pkg

import numpy as np
import matplotlib.pyplot as plt

from fooof.tests.utils import get_fm, get_fg

import pytest

###################################################################################################
###################################################################################################

def pytest_configure(config):
    plt.switch_backend('agg')
    np.random.seed(42)

@pytest.fixture(scope='session', autouse=True)
def check_dir():
    """Once, prior to session, this will clear and re-initialize the test file directories."""

    rep_dir_name = pkg.resource_filename(__name__, 'test_reports')
    dat_dir_name = pkg.resource_filename(__name__, 'test_files')

    # If the directories already exist, clear them
    if os.path.exists(rep_dir_name):
        shutil.rmtree(rep_dir_name)
    if os.path.exists(dat_dir_name):
        shutil.rmtree(dat_dir_name)

    # Remake (empty) directories
    os.mkdir(rep_dir_name)
    os.mkdir(dat_dir_name)

@pytest.fixture(scope='session')
def tfm():
    yield get_fm()

@pytest.fixture(scope='session')
def tfg():
    yield get_fg()
