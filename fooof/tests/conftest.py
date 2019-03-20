"""Configuration file for pytest."""

import os
import shutil
import pytest
import pkg_resources as pkg

import numpy as np

from fooof.core.modutils import safe_import
from fooof.tests.utils import get_tfm, get_tfg, get_tbands

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def pytest_configure(config):
    if plt:
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
    yield get_tfm()

@pytest.fixture(scope='session')
def tfg():
    yield get_tfg()

@pytest.fixture(scope='session')
def tbands():
    yield get_tbands()

@pytest.fixture(scope='session')
def skip_if_no_mpl():
    if not safe_import('matplotlib'):
        pytest.skip('Matplotlib not availabe: skipping test.')
