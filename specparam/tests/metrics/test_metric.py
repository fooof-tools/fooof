"""Tests for specparam.metrics.metric"""

from specparam.metrics.error import compute_mean_abs_error
from specparam.metrics.gof import compute_adj_r_squared

from specparam.metrics.metric import *

###################################################################################################
###################################################################################################

def test_metric(tfm):

    metric = Metric('error', 'mae', 'Description.', compute_mean_abs_error)
    assert isinstance(metric, Metric)
    assert isinstance(metric.label, str)

    metric.compute_metric(tfm.data, tfm.results)
    assert isinstance(metric.result, float)

def test_metric_kwargs(tfm):

    metric = Metric('gof', 'ar2', 'Description.', compute_adj_r_squared,
                    {'n_params' : lambda data, results: \
                        results.params.periodic.params.size + results.params.aperiodic.params.size})

    assert isinstance(metric, Metric)
    assert isinstance(metric.label, str)

    metric.compute_metric(tfm.data, tfm.results)
    assert isinstance(metric.result, float)
