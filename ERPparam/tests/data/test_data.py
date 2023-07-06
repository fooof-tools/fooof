"""Tests for the fooof.data.data.

For testing the data objects, the testing approach is to check that the object
has the expected fields, given what is defined in the object description.
"""

from fooof.core.items import OBJ_DESC

from fooof.data.data import *

###################################################################################################
###################################################################################################

def test_fooof_settings():

    settings = FOOOFSettings([1, 8], 8, 0.25, 2, 'fixed')
    assert settings

    for field in OBJ_DESC['settings']:
        assert getattr(settings, field)

def test_fooof_meta_data():

    meta_data = FOOOFMetaData([1, 50], 0.5)
    assert meta_data

    for field in OBJ_DESC['meta_data']:
        assert getattr(meta_data, field)

def test_fooof_results():

    results = FOOOFResults([1, 1], [10, 0.5, 1], 0.95, 0.05, [10, 0.5, 0.5])
    assert results

    results_fields = OBJ_DESC['results']
    for field in results_fields:
        assert getattr(results, field.strip('_'))

def test_sim_params():

    sim_params = SimParams([1, 1], [10, 1, 1], 0.05)
    assert sim_params

    for field in ['aperiodic_params', 'periodic_params', 'nlv']:
        assert getattr(sim_params, field)
