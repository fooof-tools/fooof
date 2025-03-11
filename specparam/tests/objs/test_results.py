"""Tests for specparam.objs.results, including the data object and it's methods."""

from specparam.core.items import OBJ_DESC
from specparam.data import ModelSettings

from specparam.objs.results import *

###################################################################################################
###################################################################################################

## 1D results object

def test_base_results():

    tres1 = BaseResults(None, None)
    assert isinstance(tres1, BaseResults)

    tres2 = BaseResults(aperiodic_mode='fixed', periodic_mode='gaussian')
    assert isinstance(tres2, BaseResults)

def test_base_results_settings():

    tres = BaseResults(None, None)

    settings = ModelSettings([1, 4], 6, 0, 2, 'fixed')
    tres.add_settings(settings)
    for setting in OBJ_DESC['settings']:
        assert getattr(tres, setting) == getattr(settings, setting)

    settings_out = tres.get_settings()
    assert isinstance(settings, ModelSettings)
    assert settings_out == settings

def test_base_results_results(tresults):

    tres = BaseResults(None, None)

    tres.add_results(tresults)
    assert tres.has_model
    for result in OBJ_DESC['results']:
        assert np.array_equal(getattr(tres, result), getattr(tresults, result.strip('_')))

    results_out = tres.get_results()
    assert isinstance(tresults, FitResults)
    assert results_out == tresults

## 2D results object

def test_base_results2d():

    tres2d1 = BaseResults2D(None, None)
    assert isinstance(tres2d1, BaseResults)
    assert isinstance(tres2d1, BaseResults2D)

    tres2d2 = BaseResults2D(aperiodic_mode='fixed', periodic_mode='gaussian')
    assert isinstance(tres2d2, BaseResults2D)

def test_base_results2d_results(tresults):

    tres2d = BaseResults2D(None, None)

    results = [tresults, tresults]
    tres2d.add_results(results)
    assert tres2d.has_model
    results_out = tres2d.get_results()
    assert isinstance(results_out, list)
    assert results_out == results

## 2DT results object

def test_base_results2dt():

    tres2dt1 = BaseResults2DT(None, None)
    assert isinstance(tres2dt1, BaseResults)
    assert isinstance(tres2dt1, BaseResults2D)
    assert isinstance(tres2dt1, BaseResults2DT)

    tres2dt2 = BaseResults2DT(aperiodic_mode='fixed', periodic_mode='gaussian')
    assert isinstance(tres2dt2, BaseResults2DT)

def test_base_results2d_results(tresults):

    tres2dt = BaseResults2DT(None, None)

    results = [tresults, tresults]
    tres2dt.add_results(results)
    tres2dt.convert_results(None)

    assert tres2dt.has_model
    results_out = tres2dt.get_results()
    assert isinstance(results_out, dict)

## 3D results object

def test_base_results3d():

    tres3d1 = BaseResults3D(None, None)
    assert isinstance(tres3d1, BaseResults)
    assert isinstance(tres3d1, BaseResults2D)
    assert isinstance(tres3d1, BaseResults2DT)
    assert isinstance(tres3d1, BaseResults3D)

    tres3d2 = BaseResults3D(aperiodic_mode='fixed', periodic_mode='gaussian')
    assert isinstance(tres3d2, BaseResults3D)

def test_base_results3d_results(tresults):

    tres3d = BaseResults3D(None, None)

    eresults = [[tresults, tresults], [tresults, tresults]]
    tres3d.add_results(eresults)
    tres3d.convert_results(None)

    assert tres3d.has_model
    results_out = tres3d.get_results()
    assert isinstance(results_out, dict)
