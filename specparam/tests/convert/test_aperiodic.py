"""Test functions for specparam.convert.aperiodic."""

from specparam.convert.aperiodic import *

###################################################################################################
###################################################################################################

def test_compute_knee_frequency():

    assert compute_knee_frequency(100, 2)

def test_compute_time_constant():

    assert compute_time_constant(10)
