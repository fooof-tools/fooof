"""Tests for fooof.core.strings."""

from fooof.core.strings import *

###################################################################################################
###################################################################################################

def test_gen_bw_warn_str():

    assert gen_bw_warn_str(0.5, 0.5)

def test_gen_settings_str(tfm):

    assert gen_settings_str(tfm)

def test_gen_results_str_fm(tfm):

    assert gen_results_str_fm(tfm)

def test_gen_results_str_fg(tfg):

    assert gen_results_str_fg(tfg)

def test_gen_report_str():

    assert gen_report_str()
