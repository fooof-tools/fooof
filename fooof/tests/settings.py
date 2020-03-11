"""Settings for testing fooof."""

import os
import pkg_resources as pkg

###################################################################################################
###################################################################################################

# Path Settings
BASE_TEST_FILE_PATH = pkg.resource_filename(__name__, 'test_files')
TEST_DATA_PATH = os.path.join(BASE_TEST_FILE_PATH, 'data')
TEST_REPORTS_PATH = os.path.join(BASE_TEST_FILE_PATH, 'reports')
