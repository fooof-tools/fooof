"""Tests for specparam.results.results."""

from specparam.results.results import *

###################################################################################################
###################################################################################################

## 1D results object

def test_results():

    tres = Results()
    assert isinstance(tres, Results)

def test_results_results(tresults, tmodes):

    tres = Results()

    tres.add_results(tresults)
    assert tres.has_model
    for component in tmodes.components:
        attr_comp = 'peak' if component == 'periodic' else component
        assert np.array_equal(getattr(tres.params, component).get_params('fit'),
                              getattr(tresults, attr_comp + '_fit'))

    results_out = tres.get_results()
    assert results_out == tresults

## 2D results object

def test_results2d():

    tres2d1 = Results2D()
    assert isinstance(tres2d1, Results)
    assert isinstance(tres2d1, Results2D)

def test_results2d_results(tresults, tmodes):

    tres2d = Results2D(modes=tmodes)

    results = [tresults, tresults]
    tres2d.add_results(results)
    assert tres2d.has_model
    results_out = tres2d.get_results()
    assert isinstance(results_out, list)
    assert results_out == results

## 2DT results object

def test_results2dt():

    tres2dt1 = Results2DT()
    assert isinstance(tres2dt1, Results)
    assert isinstance(tres2dt1, Results2D)
    assert isinstance(tres2dt1, Results2DT)

def test_results2dt_results(tresults, tmodes):

    tres2dt = Results2DT(modes=tmodes)

    results = [tresults, tresults]
    tres2dt.add_results(results)
    tres2dt.convert_results()

    assert tres2dt.has_model
    results_out = tres2dt.get_results()
    assert isinstance(results_out, dict)

## 3D results object

def test_results3d():

    tres3d1 = Results3D()
    assert isinstance(tres3d1, Results)
    assert isinstance(tres3d1, Results2D)
    assert isinstance(tres3d1, Results2DT)
    assert isinstance(tres3d1, Results3D)

def test_results3d_results(tresults, tmodes):

    tres3d = Results3D(modes=tmodes)

    eresults = [[tresults, tresults], [tresults, tresults]]
    tres3d.add_results(eresults)
    tres3d.convert_results()

    assert tres3d.has_model
    results_out = tres3d.get_results()
    assert isinstance(results_out, dict)
