"""Tests for specparam.objs.model, including the model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np
from pytest import raises

from specparam.core.items import OBJ_DESC
from specparam.utils.select import groupby
from specparam.modutils.errors import FitError
from specparam.sim import gen_freqs, sim_power_spectrum
from specparam.data import FitResults
from specparam.modutils.dependencies import safe_import
from specparam.modutils.errors import DataError, NoDataError, InconsistentDataError

pd = safe_import('pandas')

from specparam.tests.tsettings import TEST_DATA_PATH
from specparam.tests.tdata import default_spectrum_params, get_tfm
from specparam.tests.tutils import plot_test

from specparam.objs.model import *

###################################################################################################
###################################################################################################

def test_model_object():
    """Check model object initializes properly."""

    assert SpectralModel(verbose=False)

def test_has_data(tfm):
    """Test the has_data property attribute, with and without model fits."""

    assert tfm.has_data

    ntfm = SpectralModel()
    assert not ntfm.has_data

def test_has_model(tfm):
    """Test the has_model property attribute, with and without model fits."""

    assert tfm.has_model

    ntfm = SpectralModel()
    assert not ntfm.has_model

def test_n_peaks(tfm):
    """Test the n_peaks property attribute."""

    assert tfm.n_peaks_

def test_fit_nk():
    """Test fit, no knee."""

    ap_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]
    nlv = 0.0025

    xs, ys = sim_power_spectrum([3, 50], ap_params, gauss_params, nlv)

    tfm = SpectralModel(verbose=False)
    tfm.fit(xs, ys)

    # Check model results - aperiodic parameters
    assert np.allclose(ap_params, tfm.aperiodic_params_, [0.5, 0.1])

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(groupby(gauss_params, 3)):
        assert np.allclose(gauss, tfm.gaussian_params_[ii], [2.0, 0.5, 1.0])

def test_fit_nk_noise():
    """Test fit on noisy data, to make sure nothing breaks."""

    nlv = 1.0
    xs, ys = sim_power_spectrum(*default_spectrum_params(), nlv=nlv)

    tfm = SpectralModel(max_n_peaks=8, verbose=False)
    tfm.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfm.has_model

def test_fit_knee():
    """Test fit, with a knee."""

    ap_params = [50, 10, 1]
    gauss_params = [10, 0.3, 2, 20, 0.1, 4, 60, 0.3, 1]
    nlv = 0.0025

    xs, ys = sim_power_spectrum([1, 150], ap_params, gauss_params, nlv)

    tfm = SpectralModel(aperiodic_mode='knee', verbose=False)
    tfm.fit(xs, ys)

    # Check model results - aperiodic parameters
    assert np.allclose(ap_params, tfm.aperiodic_params_, [1, 2, 0.2])

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(groupby(gauss_params, 3)):
        assert np.allclose(gauss, tfm.gaussian_params_[ii], [2.0, 0.5, 1.0])

def test_fit_measures():
    """Test goodness of fit & error metrics, post model fitting."""

    tfm = SpectralModel(verbose=False)

    # Hack fake data with known properties: total error magnitude 2
    tfm.power_spectrum = np.array([1, 2, 3, 4, 5])
    tfm.modeled_spectrum_ = np.array([1, 2, 5, 4, 5])

    # Check default goodness of fit and error measures
    tfm._calc_r_squared()
    assert np.isclose(tfm.r_squared_, 0.75757575)
    tfm._calc_error()
    assert np.isclose(tfm.error_, 0.4)

    # Check with alternative error fit approach
    tfm._calc_error(metric='MSE')
    assert np.isclose(tfm.error_, 0.8)
    tfm._calc_error(metric='RMSE')
    assert np.isclose(tfm.error_, np.sqrt(0.8))

def test_checks():
    """Test various checks, errors and edge cases for model fitting.
    This tests all the input checking done in `_prepare_data`.
    """

    xs, ys = sim_power_spectrum(*default_spectrum_params())
    tfm = SpectralModel(verbose=False)

    ## Check checks & errors done in `_prepare_data`

    # Check wrong data type error
    with raises(DataError):
        tfm.fit(list(xs), list(ys))

    # Check dimension error
    with raises(DataError):
        tfm.fit(xs, np.reshape(ys, [1, len(ys)]))

    # Check shape mismatch error
    with raises(InconsistentDataError):
        tfm.fit(xs[:-1], ys)

    # Check complex inputs error
    with raises(DataError):
        tfm.fit(xs, ys.astype('complex'))

    # Check trim_spectrum range
    tfm.fit(xs, ys, [3, 40])

    # Check freq of 0 issue
    xs, ys = sim_power_spectrum(*default_spectrum_params())
    tfm.fit(xs, ys)
    assert tfm.freqs[0] != 0

    # Check error for `check_freqs` - for if there is non-even frequency values
    with raises(DataError):
        tfm.fit(np.array([1, 2, 4]), np.array([1, 2, 3]))

    # Check error for `check_data` - for if there is a post-logging inf or nan
    with raises(DataError):  # Double log (1) -> -inf
        tfm.fit(np.array([1, 2, 3]), np.log10(np.array([1, 2, 3])))
    with raises(DataError):  # Log (-1) -> NaN
        tfm.fit(np.array([1, 2, 3]), np.array([-1, 2, 3]))

    ## Check errors & errors done in `fit`

    # Check fit, and string report model error (no data / model fit)
    tfm = SpectralModel(verbose=False)
    with raises(NoDataError):
        tfm.fit()

def test_load():
    """Test loading data into model object. Note: loads files from test_core_io."""

    # Test loading just results
    tfm = SpectralModel(verbose=False)
    file_name_res = 'test_model_res'
    tfm.load(file_name_res, TEST_DATA_PATH)
    # Check that result attributes get filled
    for result in OBJ_DESC['results']:
        assert not np.all(np.isnan(getattr(tfm, result)))
    # Test that settings and data are None
    #   Except for aperiodic mode, which can be inferred from the data
    for setting in OBJ_DESC['settings']:
        if setting != 'aperiodic_mode':
            assert getattr(tfm, setting) is None
    assert getattr(tfm, 'power_spectrum') is None

    # Test loading just settings
    tfm = SpectralModel(verbose=False)
    file_name_set = 'test_model_set'
    tfm.load(file_name_set, TEST_DATA_PATH)
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is not None
    # Test that results and data are None
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))
    assert tfm.power_spectrum is None

    # Test loading just data
    tfm = SpectralModel(verbose=False)
    file_name_dat = 'test_model_dat'
    tfm.load(file_name_dat, TEST_DATA_PATH)
    assert tfm.power_spectrum is not None
    # Test that settings and results are None
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is None
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))

    # Test loading all elements
    tfm = SpectralModel(verbose=False)
    file_name_all = 'test_model_all'
    tfm.load(file_name_all, TEST_DATA_PATH)
    for result in OBJ_DESC['results']:
        assert not np.all(np.isnan(getattr(tfm, result)))
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is not None
    for data in OBJ_DESC['data']:
        assert getattr(tfm, data) is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm, meta_dat) is not None

def test_add_data():
    """Tests method to add data to model objects."""

    # This test uses it's own model object, to not add stuff to the global one
    tfm = get_tfm()

    # Test data for adding
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])

    # Test adding data
    tfm.add_data(freqs, pows)
    assert tfm.has_data
    assert np.all(tfm.freqs == freqs)
    assert np.all(tfm.power_spectrum == np.log10(pows))

    # Test that prior data does not get cleared, when requesting not to clear
    tfm._reset_data_results(True, True, True)
    tfm.add_results(FitResults([1, 1], [10, 0.5, 0.5], 0.95, 0.02, [10, 0.5, 0.25]))
    tfm.add_data(freqs, pows, clear_results=False)
    assert tfm.has_data
    assert tfm.has_model

    # Test that prior data does get cleared, when requesting not to clear
    tfm._reset_data_results(True, True, True)
    tfm.add_data(freqs, pows, clear_results=True)
    assert tfm.has_data
    assert not tfm.has_model

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

def test_get_data(tfm):

    for comp in ['full', 'aperiodic', 'peak']:
        for space in ['log', 'linear']:
            assert isinstance(tfm.get_data(comp, space), np.ndarray)

def test_get_model(tfm):

    for comp in ['full', 'aperiodic', 'peak']:
        for space in ['log', 'linear']:
            assert isinstance(tfm.get_model(comp, space), np.ndarray)

def test_prints(tfm):
    """Test methods that print (alias and pass through methods).

    Checks: print_settings, print_results, print_report_issue.
    """

    tfm.print_settings()
    tfm.print_results()
    tfm.print_report_issue()

@plot_test
def test_plot(tfm, skip_if_no_mpl):
    """Check the alias to plot spectra & model results."""

    tfm.plot()

def test_resets():
    """Check that all relevant data is cleared in the reset method."""

    # Note: uses it's own tfm, to not clear the global one
    tfm = get_tfm()

    tfm._reset_data_results(True, True, True)
    tfm._reset_internal_settings()

    for data in ['data', 'model_components']:
        for field in OBJ_DESC[data]:
            assert getattr(tfm, field) is None
    for field in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, field)))
    assert tfm.freqs is None and tfm.modeled_spectrum_ is None

def test_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    tfm = SpectralModel(verbose=False)
    tfm.report(*sim_power_spectrum(*default_spectrum_params()))

    assert tfm

def test_fit_failure():
    """Test model fit failures."""

    ## Induce a runtime error, and check it runs through
    tfm = SpectralModel(verbose=False)
    tfm._maxfev = 2

    tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

    # Check after failing out of fit, all results are reset
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))

    ## Monkey patch to check errors in general
    #  This mimics the main fit-failure, without requiring bad data / waiting for it to fail.
    tfm = SpectralModel(verbose=False)
    def raise_runtime_error(*args, **kwargs):
        raise FitError('Test-MonkeyPatch')
    tfm._fit_peaks = raise_runtime_error

    # Run a model fit - this should raise an error, but continue in try/except
    tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

    # Check after failing out of fit, all results are reset
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))

def test_debug():
    """Test model object in debug mode, including with fit failures."""

    tfm = SpectralModel(verbose=False)
    tfm._maxfev = 2

    tfm.set_debug_mode(True)
    assert tfm._debug is True

    with raises(FitError):
        tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

def test_set_check_modes():
    """Test changing check_modes using set_check_modes, and that checks get turned off.
    Note that testing for checks raising errors happens in test_checks.`"""

    tfm = SpectralModel(verbose=False)
    tfm.set_check_modes(False, False)

    # Add bad frequency data, with check freqs turned off
    freqs = np.array([1, 2, 4])
    powers = np.array([1, 2, 3])
    tfm.add_data(freqs, powers)
    assert tfm.has_data

    # Add bad power values data, with check data turned off
    freqs = gen_freqs([3, 30], 1)
    powers = np.ones_like(freqs) * np.nan
    tfm.add_data(freqs, powers)
    assert tfm.has_data

    # Model fitting should execute, but return a null model fit, given the NaNs, without failing
    tfm.fit()
    assert not tfm.has_model

    # Reset check modes to true
    tfm.set_check_modes(True, True)
    assert tfm._check_freqs is True
    assert tfm._check_data is True

def test_to_df(tfm, tbands, skip_if_no_pandas):

    df1 = tfm.to_df(2)
    assert isinstance(df1, pd.Series)
    df2 = tfm.to_df(tbands)
    assert isinstance(df2, pd.Series)
