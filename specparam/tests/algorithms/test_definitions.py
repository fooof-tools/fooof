"""Tests for specparam.algorithms.definitions."""

from specparam.algorithms.definitions import *

###################################################################################################
###################################################################################################

def test_check_algorithm_definition():

    for algorithm in ALGORITHMS.keys():
        algorithm = check_algorithm_definition(algorithm, ALGORITHMS)
        assert issubclass(algorithm, Algorithm)
