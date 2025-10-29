"""Tests for specparam.metrics.metrics"""

from pytest import raises

from specparam.metrics.metric import Metric
from specparam.metrics.error import compute_mean_abs_error
from specparam.metrics.gof import compute_r_squared, compute_adj_r_squared

from specparam.metrics.metrics import *

###################################################################################################
###################################################################################################

def test_metrics_null():

    metrics = Metrics()
    assert isinstance(metrics, Metrics)

def test_metrics_obj(tfm):

    er_metric = Metric('error', 'mae', 'Description.', compute_mean_abs_error)
    gof_metric = Metric('gof', 'rsquared', 'Description.', compute_r_squared)

    metrics = Metrics([er_metric, gof_metric])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.results, dict)

    # Check indexing
    met_out = metrics['error_mae']
    assert isinstance(met_out, Metric)
    with raises(ValueError):
        metrics['bad-label']

    # Check getting metrics out
    out1 = metrics.get_metrics('error')
    assert out1 == metrics.results['error_mae']
    out2 = metrics.get_metrics('gof', 'rsquared')
    assert out2 == metrics.results['gof_rsquared']

def test_metrics_dict(tfm):

    er_met_def = {'category' : 'error', 'measure' : 'mae',
                  'description' : 'Description.', 'func' : compute_mean_abs_error}
    gof_met_def = {'category' : 'gof', 'measure' : 'rsquared',
                   'description' : 'Description.', 'func' : compute_r_squared}

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

    er_met_def = {'category' : 'error', 'measure' : 'mae',
                  'description' : 'Description.', 'func' : compute_mean_abs_error}
    ar2_met_def = {'category' : 'gof', 'measure' : 'arsquared',
                   'description' : 'Description.',
                   'func' : compute_adj_r_squared,
                   'kwargs' : {'n_params' : lambda data, results: \
                        results.params.periodic.params.size + results.params.aperiodic.params.size}}

    metrics = Metrics([er_met_def, ar2_met_def])
    assert isinstance(metrics, Metrics)

    metrics.compute_metrics(tfm.data, tfm.results)
    assert isinstance(metrics.results, dict)
