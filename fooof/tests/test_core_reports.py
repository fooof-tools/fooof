"""Tests for fooof.core.reports."""

import os
import pkg_resources as pkg

from fooof.core.reports import *

###################################################################################################
###################################################################################################

def test_create_report_fm(tfm):

    file_name = 'test_report'
    file_path = pkg.resource_filename(__name__, 'test_reports')

    create_report_fm(tfm, file_name, file_path)

    assert os.path.exists(os.path.join(file_path, file_name + '.pdf'))

def test_create_report_fg(tfg):

    file_name = 'test_group_report'
    file_path = pkg.resource_filename(__name__, 'test_reports')

    create_report_fg(tfg, file_name, file_path)

    assert os.path.exists(os.path.join(file_path, file_name + '.pdf'))
