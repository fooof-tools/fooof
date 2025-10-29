"""Test functions for specparam.metrics.definitions."""

from specparam.metrics.metrics import Metric

from specparam.metrics.definitions import *

###################################################################################################
###################################################################################################

def test_metrics_library():

    for key in METRICS:
        assert isinstance(METRICS[key], Metric)
