"""Test functions for specparam.metrics.definitions."""

from specparam.metrics.metrics import Metric

from specparam.metrics.definitions import *

###################################################################################################
###################################################################################################

def test_metrics_library():

    for key, metric in METRICS.items():
        assert isinstance(metric, Metric)
        assert metric.label == key

def test_check_metrics():

    check_metrics()
