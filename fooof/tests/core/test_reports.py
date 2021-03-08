"""Tests for fooof.core.reports."""

import os

from fooof.tests.settings import TEST_REPORTS_PATH

from fooof.core.reports import *

###################################################################################################
###################################################################################################

def test_save_report_fm(tfm, skip_if_no_mpl):

    file_name = os.path.join(TEST_REPORTS_PATH, 'test_report')

    save_report_fm(tfm, file_name)

    assert os.path.exists(os.path.join(TEST_REPORTS_PATH, file_name + '.pdf'))

def test_save_report_fg(tfg, skip_if_no_mpl):

    file_name = os.path.join(TEST_REPORTS_PATH, 'test_group_report')

    save_report_fg(tfg, file_name)

    assert os.path.exists(file_name + '.pdf')
