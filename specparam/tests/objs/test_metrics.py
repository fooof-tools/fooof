"""Tests for specparam.objs.metrics."""

from specparam.measures.error import compute_mean_abs_error
from specparam.measures.gof import compute_r_squared

from specparam.objs.metrics import *

###################################################################################################
###################################################################################################

def test_metric(tfm):

    metric = Metric('error', 'mae', compute_mean_abs_error)
    assert isinstance(metric, Metric)
    assert isinstance(metric.label, str)

    metric.compute_metric(tfm.data, tfm.results)
    assert isinstance(metric.output, float)

def test_metrics_null():

    metrics = Metrics()
    assert isinstance(metrics, Metrics)

def test_metrics_obj(tfm):

    er_metric = Metric('error', 'mae', compute_mean_abs_error)
    gof_metric = Metric('gof', 'r_squared', compute_r_squared)

    metrics = Metrics([er_metric, gof_metric])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.outputs, dict)

def test_metrics_dict(tfm):

    er_met_def = {'measure' : 'error', 'metric' : 'mae', 'func' : compute_mean_abs_error}
    gof_met_def = {'measure' : 'gof', 'metric' : 'r_squared', 'func' : compute_r_squared}

    metrics = Metrics([er_met_def, gof_met_def])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.outputs, dict)
