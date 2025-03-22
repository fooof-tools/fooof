"""Tests for specparam.objs.results, including the data object and it's methods."""

from specparam.modes.items import OBJ_DESC

from specparam.objs.results import *

###################################################################################################
###################################################################################################

## 1D results object

def test_base_results():

    tres1 = BaseResults()
    assert isinstance(tres1, BaseResults)

def test_base_results_results(tresults):

    tres = BaseResults()

    tres.add_results(tresults)
    assert tres.has_model
    for result in OBJ_DESC['results']:
        assert np.array_equal(getattr(tres, result), getattr(tresults, result.strip('_')))

    results_out = tres.get_results()
    assert isinstance(tresults, FitResults)
    assert results_out == tresults

## 2D results object

def test_base_results2d():

    tres2d1 = BaseResults2D()
    assert isinstance(tres2d1, BaseResults)
    assert isinstance(tres2d1, BaseResults2D)

def test_base_results2d_results(tresults):

    tres2d = BaseResults2D()

    results = [tresults, tresults]
    tres2d.add_results(results)
    assert tres2d.has_model
    results_out = tres2d.get_results()
    assert isinstance(results_out, list)
    assert results_out == results

## 2DT results object

def test_base_results2dt():

    tres2dt1 = BaseResults2DT()
    assert isinstance(tres2dt1, BaseResults)
    assert isinstance(tres2dt1, BaseResults2D)
    assert isinstance(tres2dt1, BaseResults2DT)

def test_base_results2d_results(tresults):

    tres2dt = BaseResults2DT()

    results = [tresults, tresults]
    tres2dt.add_results(results)
    tres2dt.convert_results(None)

    assert tres2dt.has_model
    results_out = tres2dt.get_results()
    assert isinstance(results_out, dict)

## 3D results object

def test_base_results3d():

    tres3d1 = BaseResults3D()
    assert isinstance(tres3d1, BaseResults)
    assert isinstance(tres3d1, BaseResults2D)
    assert isinstance(tres3d1, BaseResults2DT)
    assert isinstance(tres3d1, BaseResults3D)

def test_base_results3d_results(tresults):

    tres3d = BaseResults3D()

    eresults = [[tresults, tresults], [tresults, tresults]]
    tres3d.add_results(eresults)
    tres3d.convert_results(None)

    assert tres3d.has_model
    results_out = tres3d.get_results()
    assert isinstance(results_out, dict)
