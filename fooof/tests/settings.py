"""Settings for testing fooof."""

import os

# Use importlib to get package related paths, importing depending on Python version
#   Note: can drop if/else when support goes to >= 3.9 (see: https://stackoverflow.com/a/75503824)
import sys
if sys.version_info >= (3, 9):
    import importlib.resources as importlib_resources
else:
    import importlib_resources

###################################################################################################
###################################################################################################

# Path Settings
BASE_TEST_FILE_PATH = importlib_resources.files(__name__.split('.')[0]) / 'tests/test_files'
TEST_DATA_PATH = os.path.join(BASE_TEST_FILE_PATH, 'data')
TEST_REPORTS_PATH = os.path.join(BASE_TEST_FILE_PATH, 'reports')
TEST_PLOTS_PATH = os.path.join(BASE_TEST_FILE_PATH, 'plots')
