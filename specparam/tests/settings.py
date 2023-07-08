"""Settings for testing spectral parameterization."""

import os
from pathlib import Path

###################################################################################################
###################################################################################################

# Path Settings
TESTS_PATH = Path(os.path.abspath(os.path.dirname(__file__)))
BASE_TEST_FILE_PATH = TESTS_PATH / 'test_files'
TEST_DATA_PATH = BASE_TEST_FILE_PATH / 'data'
TEST_REPORTS_PATH = BASE_TEST_FILE_PATH / 'reports'
TEST_PLOTS_PATH = BASE_TEST_FILE_PATH / 'plots'
