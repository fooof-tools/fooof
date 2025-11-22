"""Configuration file for pytest."""

import os
import shutil
import pytest

import numpy as np

from specparam.modutils.dependencies import safe_import

from specparam.tests.tdata import (get_tdata, get_tdata2d, get_tdata2dt, get_tdata3d,
                                   get_tfm, get_tfm2, get_tfg, get_tfg2, get_tft, get_tfe,
                                   get_tbands, get_tresults, get_tmodes, get_tdocstring)
from specparam.tests.tsettings import (BASE_TEST_FILE_PATH, TEST_DATA_PATH,
                                       TEST_REPORTS_PATH, TEST_PLOTS_PATH)

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

## TEST SETUP

def pytest_configure(config):
    if plt:
        plt.switch_backend('agg')
    np.random.seed(13)

@pytest.fixture(scope='session', autouse=True)
def check_dir():
    """Once, prior to session, this will clear and re-initialize the test file directories."""

    # If the directories already exist, clear them
    if os.path.exists(BASE_TEST_FILE_PATH):
        shutil.rmtree(BASE_TEST_FILE_PATH)

    # Remake (empty) directories
    os.mkdir(BASE_TEST_FILE_PATH)
    os.mkdir(TEST_DATA_PATH)
    os.mkdir(TEST_REPORTS_PATH)
    os.mkdir(TEST_PLOTS_PATH)

## DEPENDENCY CHECKS

@pytest.fixture(scope='session')
def skip_if_no_mpl():
    if not safe_import('matplotlib'):
        pytest.skip('Matplotlib not available: skipping test.')

@pytest.fixture(scope='session')
def skip_if_no_tqdm():
    if not safe_import('tqdm'):
        pytest.skip('tqdm not available: skipping test.')

@pytest.fixture(scope='session')
def skip_if_no_pandas():
    if not safe_import('pandas'):
        pytest.skip('Pandas not available: skipping test.')

## TEST OBJECTS

@pytest.fixture(scope='session')
def tdata():
    yield get_tdata()

@pytest.fixture(scope='session')
def tdata2d():
    yield get_tdata2d()

@pytest.fixture(scope='session')
def tdata2dt():
    yield get_tdata2dt()

@pytest.fixture(scope='session')
def tdata3d():
    yield get_tdata3d()

@pytest.fixture(scope='session')
def tfm():
    yield get_tfm()

@pytest.fixture(scope='session')
def tfm2():
    yield get_tfm2()

@pytest.fixture(scope='session')
def tfg():
    yield get_tfg()

@pytest.fixture(scope='session')
def tfg2():
    yield get_tfg2()

@pytest.fixture(scope='session')
def tft():
    yield get_tft()

@pytest.fixture(scope='session')
def tfe():
    yield get_tfe()

@pytest.fixture(scope='session')
def tbands():
    yield get_tbands()

@pytest.fixture(scope='session')
def tresults():
    yield get_tresults()

@pytest.fixture(scope='session')
def tmodes():
    yield get_tmodes()

@pytest.fixture(scope='function')
def tdocstring():
    yield get_tdocstring()
