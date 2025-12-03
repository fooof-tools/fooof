"""Tests for specparam.reports.strings."""

from specparam.reports.strings import *
from specparam.reports.strings import _format, _no_model_str

###################################################################################################
###################################################################################################

def test_gen_width_warning_str():

    assert gen_width_warning_str(0.5, 0.5)

def test_gen_version_str():

    assert gen_version_str()

def test_gen_data_str(tdata, tdata2d, tdata2dt, tdata3d):

    assert gen_data_str(tdata)
    assert gen_data_str(tdata2d)
    assert gen_data_str(tdata2dt)
    assert gen_data_str(tdata3d)

def test_gen_modes_str(tfm):

    assert gen_modes_str(tfm.modes)
    assert gen_modes_str(tfm.modes, True)

def test_gen_settings_str(tfm):

    assert gen_settings_str(tfm.algorithm)
    assert gen_settings_str(tfm.algorithm, True)

def test_gen_metrics_str(tfm):

    assert gen_metrics_str(tfm.results.metrics)
    assert gen_metrics_str(tfm.results.metrics, True)

def test_gen_freq_range_str(tfm):

    assert gen_freq_range_str(tfm)

def test_gen_methods_report_str():

    assert gen_methods_report_str()

def test_gen_methods_text_str(tfm):

    # Test with and without passing in a model object
    assert gen_methods_text_str()
    assert gen_methods_text_str(tfm)

def test_gen_model_results_str(tfm):

    assert gen_model_results_str(tfm)

def test_gen_group_results_str(tfg):

    assert gen_group_results_str(tfg)

def test_gen_time_results_str(tft):

    assert gen_time_results_str(tft)

def test_gen_time_results_str(tfe):

    assert gen_event_results_str(tfe)

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
