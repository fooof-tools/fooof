"""Tests for specparam.algorthms.algorithm."""

from specparam.algorithms.settings import SettingsDefinition

from specparam.algorithms.algorithm import *

###################################################################################################
###################################################################################################

def test_algorithm():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    algo = Algorithm(name=tname, description=tdescription, settings=tsettings, format='spectrum')
    assert algo
    assert algo.name == tname
    assert algo.description == tdescription
    assert isinstance(algo._settings, SettingsDefinition)
    assert algo._settings == tsettings

def test_algorithm_settings():

    tname = 'test_algo'
    tdescription = 'Test algorithm description'
    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    talgo = Algorithm(name=tname, description=tdescription, settings=tsettings, format='spectrum')

    model_settings = talgo._settings.make_model_settings()
    settings = model_settings(a=1, b=2)
    talgo.add_settings(settings)
    for setting in settings._fields:
        assert getattr(talgo, setting) == getattr(settings, setting)

    settings_out = talgo.get_settings()
    assert isinstance(settings, model_settings)
    assert settings_out == settings
