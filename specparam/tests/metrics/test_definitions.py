"""Test functions for specparam.measures.metrics."""

from specparam.objs.metrics import Metric

from specparam.measures.metrics import *

###################################################################################################
###################################################################################################

def test_metrics_library():

    for key in METRICS:
        assert isinstance(METRICS[key], Metric)
