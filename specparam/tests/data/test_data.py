"""Tests for the specparam.data.data.

For testing the data objects, the testing approach is to check that the object
has the expected fields, given what is defined in the object description.
"""

from specparam.core.items import OBJ_DESC

from specparam.data.data import *

###################################################################################################
###################################################################################################

def test_model_settings():

    settings = ModelSettings([1, 8], 8, 0.25, 2, 'fixed')
    assert settings

    for field in OBJ_DESC['settings']:
        assert getattr(settings, field)

def test_spectrum_meta_data():

    meta_data = SpectrumMetaData([1, 50], 0.5)
    assert meta_data

    for field in OBJ_DESC['meta_data']:
        assert getattr(meta_data, field)

def test_model_run_modes():

    run_modes = ModelRunModes(True, True, True)
    assert run_modes

    for field in OBJ_DESC['run_modes']:
        assert getattr(run_modes, field.strip('_'))

def test_fit_results():

    results = FitResults([1, 1], [10, 0.5, 1], 0.95, 0.05, [10, 0.5, 0.5])
    assert results

    results_fields = OBJ_DESC['results']
    for field in results_fields:
        assert getattr(results, field.strip('_'))

def test_sim_params():

    sim_params = SimParams([1, 1], [10, 1, 1], 0.05)
    assert sim_params

    for field in ['aperiodic_params', 'periodic_params', 'nlv']:
        assert getattr(sim_params, field)
