"""Test functions for fooof.utils.reports"""

from fooof.utils.reports import *

###################################################################################################
###################################################################################################

def test_methods_report_info(tfm):

    # Test with and without passing in a FOOOF object
    methods_report_info()
    methods_report_info(tfm)

def test_methods_report_text(tfm):

    # Test with and without passing in a FOOOF object
    methods_report_text()
    methods_report_text(tfm)
