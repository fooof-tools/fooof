"""Tests for the specparam.data.stores."""

import numpy as np

from specparam.data.stores import *

###################################################################################################
###################################################################################################

def test_model_settings():

    settings = ModelSettings([1, 8], 8, 0.25, 2)
    assert settings

    for field in ModelSettings._fields:
        assert getattr(settings, field)

def test_spectrum_meta_data():

    meta_data = SpectrumMetaData([1, 50], 0.5)
    assert meta_data

    for field in SpectrumMetaData._fields:
        assert getattr(meta_data, field)

def test_model_checks():

    checks = ModelChecks(True, True)
    assert checks

    for field in ModelChecks._fields:
        assert getattr(checks, field.strip('_'))

def test_fit_results():

    results = FitResults(\
        [1, 1], [np.nan, np.nan], [10, 0.5, 1], [10, 0.5, 0.5], {'a' : 0.95, 'b' : 0.05})
    assert results

    for field in FitResults._fields:
        assert getattr(results, field.strip('_'))

def test_sim_params():

    sim_params = SimParams([1, 1], [10, 1, 1], 0.05)
    assert sim_params

    for field in SimParams._fields:
        assert getattr(sim_params, field)
