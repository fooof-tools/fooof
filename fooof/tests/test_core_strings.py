"""Tests for fooof.core.strings."""

from fooof.core.strings import *
from fooof.core.strings import _format, _no_model_str

###################################################################################################
###################################################################################################

def test_gen_wid_warn_str():

    assert gen_wid_warn_str(0.5, 0.5)

def test_gen_settings_str(tfm):

    assert gen_settings_str(tfm)

def test_gen_results_str_fm(tfm):

    assert gen_results_str_fm(tfm)

def test_gen_results_str_fg(tfg):

    assert gen_results_str_fg(tfg)

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
