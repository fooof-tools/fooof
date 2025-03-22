"""Tests for specparam.algorthms.algorithm."""

from specparam.algorithms.algorithm import *

###################################################################################################
###################################################################################################

def test_settings_definition():

    tsettings = {
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    }

    settings = SettingsDefinition(tsettings)
    assert settings._settings == tsettings
    assert settings.names == list(tsettings.keys())
    assert settings.types
    assert settings.descriptions
    for label in tsettings.keys():
        assert settings.make_setting_str(label)
    assert settings.make_docstring()

def test_algorithm_definition():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = {
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    }

    algo_def = AlgorithmDefinition(name=tname, description=tdescription, settings=tsettings)
    assert algo_def
    assert algo_def.name == tname
    assert algo_def.description == tdescription
    assert algo_def.settings == tsettings

def test_algorithm():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = {
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    }

    algo = Algorithm(name=tname, description=tdescription, settings=tsettings)
    assert algo
    assert isinstance(algo.algorithm, AlgorithmDefinition)
