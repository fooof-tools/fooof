"""Tests for specparam.algorthms.algorithm."""

from specparam.data import ModelSettings
from specparam.algorithms.settings import SettingsDefinition

from specparam.algorithms.algorithm import *

###################################################################################################
###################################################################################################

def test_algorithm_definition():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    algo_def = AlgorithmDefinition(name=tname, description=tdescription, settings=tsettings)
    assert algo_def
    assert algo_def.name == tname
    assert algo_def.description == tdescription
    assert algo_def.settings == tsettings

def test_algorithm():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    algo = Algorithm(name=tname, description=tdescription, settings=tsettings)
    assert algo
    assert isinstance(algo.definition, AlgorithmDefinition)

def test_algorithm_settings():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    talgo = Algorithm(name=tname, description=tdescription, settings=tsettings)

    model_settings = talgo.definition.settings.make_model_settings()
    settings = model_settings(a=1, b=2)
    talgo.add_settings(settings)
    for setting in settings._fields:
        assert getattr(talgo, setting) == getattr(settings, setting)

    settings_out = talgo.get_settings()
    assert isinstance(settings, model_settings)
    assert settings_out == settings
