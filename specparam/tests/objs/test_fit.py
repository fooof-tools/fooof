"""Tests for specparam.objs.fit, including the data object and it's methods."""

from specparam.core.items import OBJ_DESC
from specparam.data import ModelSettings

from specparam.objs.fit import *

###################################################################################################
###################################################################################################

## 1D fit object

def test_base_fit():

    tfit1 = BaseFit(None, None)
    assert isinstance(tfit1, BaseFit)

    tfit2 = BaseFit(aperiodic_mode='fixed', periodic_mode='gaussian')
    assert isinstance(tfit2, BaseFit)

def test_base_fit_settings():

    tfit = BaseFit(None, None)

    settings = ModelSettings([1, 4], 6, 0, 2, 'fixed')
    tfit.add_settings(settings)
    for setting in OBJ_DESC['settings']:
        assert getattr(tfit, setting) == getattr(settings, setting)

    settings_out = tfit.get_settings()
    assert isinstance(settings, ModelSettings)
<<<<<<< HEAD
    assert settings_out == settings
=======
    meta_data = tfm.get_meta_data()
    assert isinstance(meta_data, SpectrumMetaData)
    results = tfm.get_results()
    assert isinstance(results, FitResults)

def test_get_components(tfm):

    # Make sure test object has been fit
    tfm.fit()

    # Test get data & model components
    for comp in ['full', 'aperiodic', 'peak']:
        for space in ['log', 'linear']:
            assert isinstance(tfm.get_data(comp, space), np.ndarray)
            assert isinstance(tfm.get_model(comp, space), np.ndarray)

def test_get_params(tfm):
    """Test the get_params method."""

    for dname in ['aperiodic_params', 'aperiodic', 'peak_params', 'peak',
                  'error', 'r_squared', 'gaussian_params', 'gaussian']:
        assert np.any(tfm.get_params(dname))

        if dname == 'aperiodic_params' or dname == 'aperiodic':
            for dtype in ['offset', 'exponent']:
                assert np.any(tfm.get_params(dname, dtype))

        if dname == 'peak_params' or dname == 'peak':
            for dtype in ['CF', 'PW', 'BW']:
                assert np.any(tfm.get_params(dname, dtype))

def test_copy():
    """Test copy model object method."""
>>>>>>> name

def test_base_fit_results(tresults):

    tfit = BaseFit(None, None)

    tfit.add_results(tresults)
    assert tfit.has_model
    for result in OBJ_DESC['results']:
        assert np.array_equal(getattr(tfit, result), getattr(tresults, result.strip('_')))

    results_out = tfit.get_results()
    assert isinstance(tresults, FitResults)
    assert results_out == tresults


## 2D fit object

def test_base_fit2d():

    tfit2d1 = BaseFit2D(None, None)
    assert isinstance(tfit2d1, BaseFit)
    assert isinstance(tfit2d1, BaseFit2D)

    tfit2d2 = BaseFit2D(aperiodic_mode='fixed', periodic_mode='gaussian')
    assert isinstance(tfit2d2, BaseFit2D)

def test_base_fit2d_results(tresults):

    tfit2d = BaseFit2D(None, None)

    results = [tresults, tresults]
    tfit2d.add_results(results)
    assert tfit2d.has_model
    results_out = tfit2d.get_results()
    assert isinstance(results, list)
    assert results_out == results
