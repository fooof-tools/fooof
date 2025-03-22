"""Tests for specparam.algorthms.settings."""

from specparam.algorithms.settings import *

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
