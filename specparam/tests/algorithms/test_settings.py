"""Tests for specparam.algorthms.settings."""

from specparam.algorithms.settings import *

###################################################################################################
###################################################################################################

def test_settings_values():

    tsettings_names = ['a', 'b']
    settings_vals = SettingsValues(tsettings_names)
    assert isinstance(settings_vals.values, dict)
    assert settings_vals.names == tsettings_names
    assert settings_vals.a is None
    assert settings_vals.b is None
    settings_vals.a = 1
    settings_vals.b = 2
    assert settings_vals.a == 1
    assert settings_vals.b == 2

    settings_vals.clear()
    assert settings_vals.a is None
    assert settings_vals.b is None

def test_settings_definition():

    tdefinitions = {
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    }

    settings_def = SettingsDefinition(tdefinitions)
    assert settings_def._definitions == tdefinitions
    assert len(settings_def) == len(tdefinitions)
    assert settings_def.names == list(tdefinitions.keys())
    assert settings_def.types
    assert settings_def.descriptions
    for label in tdefinitions.keys():
        assert settings_def.make_setting_str(label)
    assert settings_def.make_docstring()
