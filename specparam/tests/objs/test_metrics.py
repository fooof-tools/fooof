"""Tests for specparam.objs.metrics."""

from pytest import raises

from specparam.measures.error import compute_mean_abs_error
from specparam.measures.gof import compute_r_squared, compute_adj_r_squared

from specparam.objs.metrics import *

###################################################################################################
###################################################################################################

def test_metric(tfm):

    metric = Metric('error', 'mae', compute_mean_abs_error)
    assert isinstance(metric, Metric)
    assert isinstance(metric.label, str)

    metric.compute_metric(tfm.data, tfm.results)
    assert isinstance(metric.result, float)

def test_metric_kwargs(tfm):

    metric = Metric('gof', 'ar2', compute_adj_r_squared, {'results' : 'n_params_'})
    assert isinstance(metric, Metric)
    assert isinstance(metric.label, str)

    metric.compute_metric(tfm.data, tfm.results)
    assert isinstance(metric.result, float)

def test_metrics_null():

    metrics = Metrics()
    assert isinstance(metrics, Metrics)

def test_metrics_obj(tfm):

    er_metric = Metric('error', 'mae', compute_mean_abs_error)
    gof_metric = Metric('gof', 'rsquared', compute_r_squared)

    metrics = Metrics([er_metric, gof_metric])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.results, dict)

    # Check indexing
    met_out = metrics['error_mae']
    assert isinstance(met_out, Metric)
    with raises(ValueError):
        metrics['bad-label']

def test_metrics_dict(tfm):

    er_met_def = {'measure' : 'error', 'metric' : 'mae', 'func' : compute_mean_abs_error}
    gof_met_def = {'measure' : 'gof', 'metric' : 'rsquared', 'func' : compute_r_squared}

    metrics = Metrics([er_met_def, gof_met_def])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.results, dict)

    # Check adding results
    res = {'error_mae' : 0.5, 'gof_rsquared' : 0.5}
    metrics.add_results(res)
    for label in metrics.labels:
        assert metrics.results[label] == res[label]
    assert metrics.results == res

def test_metrics_kwargs(tfm):

    er_met_def = {'measure' : 'error', 'metric' : 'mae', 'func' : compute_mean_abs_error}
    ar2_met_def = {'measure' : 'gof', 'metric' : 'arsquared',
                   'func' : compute_adj_r_squared, 'additional_kwargs' : {'results' : 'n_params_'}}

    metrics = Metrics([er_met_def, ar2_met_def])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.results, dict)
