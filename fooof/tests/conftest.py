"""Configuration file for pytest."""

import os
import shutil
import pkg_resources as pkg
import matplotlib

import pytest

###################################################################################################
###################################################################################################

def pytest_configure(config):
    matplotlib.use('agg')

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
