"""Tests for specparam.algorthms.settings."""

from specparam.algorithms.settings import *

###################################################################################################
###################################################################################################

def test_settings_definition():

    tdefinitions = {
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    }

    settings = SettingsDefinition(tdefinitions)
    assert settings._definitions == tdefinitions
    assert len(settings) == len(tdefinitions)
    assert settings.names == list(tdefinitions.keys())
    assert settings.types
    assert settings.descriptions
    for label in tdefinitions.keys():
        assert settings.make_setting_str(label)
    assert settings.make_docstring()
