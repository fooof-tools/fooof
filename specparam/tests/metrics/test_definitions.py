"""Test functions for specparam.metrics.definitions."""

from specparam.metrics.metrics import Metric

from specparam.metrics.definitions import *

###################################################################################################
###################################################################################################

def test_metrics_library():

    for category, collection in METRICS.items():
        for key, metric in collection.items():
            assert isinstance(metric, Metric)
            assert metric.label == category + '_' + key

def test_check_metric_definition():

    mdict = {'category' : 'test', 'measure' : 'test',
             'description' : 'test', 'func' : lambda x: x}

    m1 = check_metric_definition(Metric(**mdict))
    assert isinstance(m1, Metric)

    m2 = check_metric_definition(mdict)
    assert isinstance(m2, Metric)

    m3 = check_metric_definition('error_mae')
    assert isinstance(m3, Metric)
