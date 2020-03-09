"""Tests for the fooof.data.data."""

from fooof.core.items import OBJ_DESC

from fooof.data.data import *

###################################################################################################
###################################################################################################

def test_fooof_settings():

    settings = FOOOFSettings([], None, None, None, None)
    assert settings

    # Check that the object has the correct fields, given the object description
    settings_fields = OBJ_DESC['settings']
    for field in settings_fields:
        getattr(settings, field)
    assert True

def test_fooof_results():

    results = FOOOFResults([], [], None, None, [])
    assert results

    # Check that the object has the correct fields, given the object description
    results_fields = OBJ_DESC['results']
    for field in results_fields:
        getattr(results, field.strip('_'))
    assert True

def test_sim_params():

    sim_params = SimParams([1, 1], [10, 1, 1], 0.05)
    assert sim_params

    # Check that the object has the correct fields
    for field in ['aperiodic_params', 'periodic_params', 'nlv']:
        getattr(sim_params, field)
    assert True
