"""Tests for fooof.core.strings."""

from fooof.core.strings import *
from fooof.core.strings import _format, _no_model_str

###################################################################################################
###################################################################################################

def test_gen_width_warning_str():

    assert gen_width_warning_str(0.5, 0.5)

def test_gen_version_str():

    assert gen_version_str()

def test_gen_settings_str(tfm):

    assert gen_settings_str(tfm)

def test_gen_freq_range_str(tfm):

    assert gen_freq_range_str(tfm)

def test_gen_methods_report_str():

    assert gen_methods_report_str()

def test_gen_methods_text_str(tfm):

    # Test with and without passing in a FOOOF object
    assert gen_methods_text_str()
    assert gen_methods_text_str(tfm)

def test_gen_results_fm_str(tfm):

    assert gen_results_fm_str(tfm)

def test_gen_results_fg_str(tfg):

    assert gen_results_fg_str(tfg)

def test_gen_issue_str():

    assert gen_issue_str()

def test_no_model_str():

    assert _no_model_str()

def test_format():

    str_lst = ['=', '', 'a', '', 'b', '', '=']

    str_out_1 = _format(str_lst, False)
    assert str_out_1
    assert str_out_1.count('\n') == 6

    str_out_2 = _format(str_lst, True)
    assert str_out_2
    assert str_out_2.count('\n') == 3
