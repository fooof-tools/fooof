"""Tests for specparam.algorthms.algorithm."""

from specparam.algorithms.algorithm import *

###################################################################################################
###################################################################################################

def tests_algorithm_definition():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = {'a' : 'a desc', 'b' : 'b desc'}

    algo_def = AlgorithmDefinition(name=tname, description=tdescription, settings=tsettings)
    assert algo_def
    assert algo_def.name == tname
    assert algo_def.description == tdescription
    assert algo_def.settings == tsettings

def test_algorithm():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = {'a' : 'a desc', 'b' : 'b desc'}

    algo = Algorithm(name=tname, description=tdescription, settings=tsettings)
    assert algo
    assert isinstance(algo.algorithm, AlgorithmDefinition)
