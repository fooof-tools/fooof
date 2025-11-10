"""Tests for specparam.algorithms.definitions."""

from specparam.algorithms.algorithm import Algorithm

from specparam.algorithms.definitions import *

###################################################################################################
###################################################################################################

def test_algorithms_library():

    for key, algorithm in ALGORITHMS.items():
        algorithm = algorithm()
        assert isinstance(algorithm, Algorithm)
        assert algorithm.name == key

def test_check_algorithms():

    check_algorithms()

def test_check_algorithm_definition():

    for algorithm in ALGORITHMS.keys():
        algorithm = check_algorithm_definition(algorithm, ALGORITHMS)
        assert issubclass(algorithm, Algorithm)
