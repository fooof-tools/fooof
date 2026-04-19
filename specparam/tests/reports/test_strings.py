"""Tests for specparam.reports.strings."""

from specparam.reports.strings import *
from specparam.reports.strings import _format, _no_model_str

###################################################################################################
###################################################################################################

## GENERAL

def test_gen_issue_str():

    assert gen_issue_str()

def test_gen_version_str():

    assert gen_version_str()

def test_gen_methods_report_str():

    assert gen_methods_report_str()

## DATA

def test_gen_freq_range_str(tfm):

    assert gen_freq_range_str(tfm)

def test_gen_data_str(tdata, tdata2d, tdata2dt, tdata3d):

    assert gen_data_str(tdata)
    assert gen_data_str(tdata2d)
    assert gen_data_str(tdata2dt)
    assert gen_data_str(tdata3d)

## MODES

def test_gen_modes_str(tfm):

    assert gen_modes_str(tfm.modes)
    assert gen_modes_str(tfm.modes, True)

def test_gen_params_str(tfm):

    assert gen_params_str(tfm.modes.aperiodic.params)
    assert gen_params_str(tfm.modes.aperiodic.params, True)

## ALGORITHM / SETTINGS

def test_gen_settings_str(tfm):

    assert gen_settings_str(tfm.algorithm)
    assert gen_settings_str(tfm.algorithm, True)

def test_gen_width_warning_str():

    assert gen_width_warning_str(0.5, 0.5)

## BANDS

def test_gen_bands_str(tbands):

    assert gen_bands_str(tbands)

## METRICS

def test_gen_metric_str_lst(tfm):

    assert isinstance(gen_metric_str_lst(tfm.results.metrics.metrics[0]), list)

def test_gen_metric_str(tfm):

    assert gen_metric_str(tfm.results.metrics.metrics[0])
    assert gen_metric_str(tfm.results.metrics.metrics[0], True)

def test_gen_metrics_str(tfm):

    assert gen_metrics_str(tfm.results.metrics)
    assert gen_metrics_str(tfm.results.metrics, True)

## METHODS REPORTING





## MODEL OBJECTS

def test_gen_model_results_str(tfm):

    assert gen_model_results_str(tfm)

def test_gen_group_results_str(tfg):

    assert gen_group_results_str(tfg)

def test_gen_time_results_str(tft):

    assert gen_time_results_str(tft)

def test_gen_time_results_str(tfe):

    assert gen_event_results_str(tfe)

def test_no_model_str():

    assert _no_model_str()

## UTILITIES

def test_format():

    str_lst = ['a', '', 'b']

    str_out_1 = _format(str_lst, False)
    assert str_out_1
    assert str_out_1.count('\n') == 6

    str_out_2 = _format(str_lst, True)
    assert str_out_2
    assert str_out_2.count('\n') == 3
