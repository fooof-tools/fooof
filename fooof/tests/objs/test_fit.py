"""Tests for fooof.objs.fit, including the FOOOF object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np
from py.test import raises

from fooof.core.items import OBJ_DESC
from fooof.core.errors import FitError
from fooof.core.utils import group_three
from fooof.sim import gen_power_spectrum
from fooof.data import FOOOFSettings, FOOOFMetaData, FOOOFResults
from fooof.core.errors import DataError, NoDataError, InconsistentDataError

from fooof.tests.settings import TEST_DATA_PATH
from fooof.tests.tutils import get_tfm, plot_test

from fooof.objs.fit import *

###################################################################################################
###################################################################################################

def test_fooof():
    """Check FOOOF object initializes properly."""

    assert FOOOF(verbose=False)

def test_fooof_has_data(tfm):
    """Test the has_data property attribute, with and without model fits."""

    assert tfm.has_data

    ntfm = FOOOF()
    assert not ntfm.has_data

def test_fooof_has_model(tfm):
    """Test the has_model property attribute, with and without model fits."""

    assert tfm.has_model

    ntfm = FOOOF()
    assert not ntfm.has_model

def test_fooof_n_peaks(tfm):
    """Test the n_peaks property attribute."""

    assert tfm.n_peaks_

def test_fooof_fit_nk():
    """Test FOOOF fit, no knee."""

    ap_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum([3, 50], ap_params, gauss_params)

    tfm = FOOOF(verbose=False)
    tfm.fit(xs, ys)

    # Check model results - aperiodic parameters
    assert np.all(np.isclose(ap_params, tfm.aperiodic_params_, [0.5, 0.1]))

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(group_three(gauss_params)):
        assert np.all(np.isclose(gauss, tfm.gaussian_params_[ii], [2.0, 0.5, 1.0]))

def test_fooof_fit_nk_noise():
    """Test FOOOF fit on noisy data, to make sure nothing breaks."""

    ap_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum([3, 50], ap_params, gauss_params, nlv=1.0)

    tfm = FOOOF(max_n_peaks=8, verbose=False)
    tfm.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfm.has_model

def test_fooof_fit_knee():
    """Test FOOOF fit, with a knee."""

    ap_params = [50, 10, 1]
    gauss_params = [10, 0.3, 2, 20, 0.1, 4, 60, 0.3, 1]

    xs, ys = gen_power_spectrum([1, 150], ap_params, gauss_params, nlv=0)

    tfm = FOOOF(aperiodic_mode='knee', verbose=False)
    tfm.fit(xs, ys)

    # Check model results - aperiodic parameters
    assert np.all(np.isclose(ap_params, tfm.aperiodic_params_, [1, 2, 0.2]))

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(group_three(gauss_params)):
        assert np.all(np.isclose(gauss, tfm.gaussian_params_[ii], [2.0, 0.5, 1.0]))

def test_fooof_fit_measures():
    """Test goodness of fit & error metrics, post model fitting."""

    tfm = FOOOF(verbose=False)

    # Hack fake data with known properties: total error magnitude 2
    tfm.power_spectrum = np.array([1, 2, 3, 4, 5])
    tfm.fooofed_spectrum_ = np.array([1, 2, 5, 4, 5])

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
    with raises(ValueError):
        tfm._calc_error(metric='BAD')

def test_fooof_checks():
    """Test various checks, errors and edge cases in FOOOF.
    This tests all the input checking done in `_prepare_data`.
    """

    xs, ys = gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2])

    tfm = FOOOF(verbose=False)

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
    xs, ys = gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2])
    tfm.fit(xs, ys)
    assert tfm.freqs[0] != 0

    # Check error if there is a post-logging inf or nan
    with raises(DataError):  # Double log (1) -> -inf
        tfm.fit(np.array([1, 2, 3]), np.log10(np.array([1, 2, 3])))
    with raises(DataError):  # Log (-1) -> NaN
        tfm.fit(np.array([1, 2, 3]), np.array([-1, 2, 3]))

    ## Check errors & errors done in `fit`

    # Check fit, and string report model error (no data / model fit)
    tfm = FOOOF(verbose=False)
    with raises(NoDataError):
        tfm.fit()

def test_fooof_load():
    """Test load into FOOOF. Note: loads files from test_core_io."""

    # Test loading just results
    tfm = FOOOF(verbose=False)
    file_name_res = 'test_fooof_res'
    tfm.load(file_name_res, TEST_DATA_PATH)
    # Check that result attributes get filled
    for result in OBJ_DESC['results']:
        assert not np.all(np.isnan(getattr(tfm, result)))
    # Test that settings and data are None
    #   Except for aperiodic mode, which can be inferred from the data
    for setting in OBJ_DESC['settings']:
        if setting is not 'aperiodic_mode':
            assert getattr(tfm, setting) is None
    assert getattr(tfm, 'power_spectrum') is None

    # Test loading just settings
    tfm = FOOOF(verbose=False)
    file_name_set = 'test_fooof_set'
    tfm.load(file_name_set, TEST_DATA_PATH)
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is not None
    # Test that results and data are None
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))
    assert tfm.power_spectrum is None

    # Test loading just data
    tfm = FOOOF(verbose=False)
    file_name_dat = 'test_fooof_dat'
    tfm.load(file_name_dat, TEST_DATA_PATH)
    assert tfm.power_spectrum is not None
    # Test that settings and results are None
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is None
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))

    # Test loading all elements
    tfm = FOOOF(verbose=False)
    file_name_all = 'test_fooof_all'
    tfm.load(file_name_all, TEST_DATA_PATH)
    for result in OBJ_DESC['results']:
        assert not np.all(np.isnan(getattr(tfm, result)))
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is not None
    for data in OBJ_DESC['data']:
        assert getattr(tfm, data) is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm, meta_dat) is not None

def test_adds():
    """Tests methods that add data to FOOOF objects.

    Checks: add_data, add_settings, add_results.
    """

    # Note: uses it's own tfm, to not add stuff to the global one
    tfm = get_tfm()

    # Test adding data
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])
    tfm.add_data(freqs, pows)
    assert np.all(tfm.freqs == freqs)
    assert np.all(tfm.power_spectrum == np.log10(pows))

    # Test adding settings
    fooof_settings = FOOOFSettings([1, 4], 6, 0, 2, 'fixed')
    tfm.add_settings(fooof_settings)
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) == getattr(fooof_settings, setting)

    # Test adding meta data
    fooof_meta_data = FOOOFMetaData([3, 40], 0.5)
    tfm.add_meta_data(fooof_meta_data)
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm, meta_dat) == getattr(fooof_meta_data, meta_dat)

    # Test adding results
    fooof_results = FOOOFResults([1, 1], [10, 0.5, 0.5], 0.95, 0.02, [10, 0.5, 0.25])
    tfm.add_results(fooof_results)
    for setting in OBJ_DESC['results']:
        assert getattr(tfm, setting) == getattr(fooof_results, setting.strip('_'))

def test_obj_gets(tfm):
    """Tests methods that return FOOOF data objects.

    Checks: get_settings, get_meta_data, get_results
    """

    settings = tfm.get_settings()
    assert isinstance(settings, FOOOFSettings)
    meta_data = tfm.get_meta_data()
    assert isinstance(meta_data, FOOOFMetaData)
    results = tfm.get_results()
    assert isinstance(results, FOOOFResults)

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
    """Test copy FOOOF method."""

    tfm = FOOOF(verbose=False)
    ntfm = tfm.copy()

    assert tfm != ntfm

def test_fooof_prints(tfm):
    """Test methods that print (alias and pass through methods).

    Checks: print_settings, print_results, print_report_issue.
    """

    tfm.print_settings()
    tfm.print_results()
    tfm.print_report_issue()

@plot_test
def test_fooof_plot(tfm, skip_if_no_mpl):
    """Check the alias to plot FOOOF."""

    tfm.plot()

def test_fooof_resets():
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
    assert tfm.freqs is None and tfm.fooofed_spectrum_ is None

def test_fooof_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    tfm = FOOOF(verbose=False)

    tfm.report(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    assert tfm

def test_fooof_fit_failure():
    """Test FOOOF fit failures."""

    ## Induce a runtime error, and check it runs through
    tfm = FOOOF(verbose=False)
    tfm._maxfev = 5

    tfm.fit(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    # Check after failing out of fit, all results are reset
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))

    ## Monkey patch to check errors in general
    #  This mimics the main fit-failure, without requiring bad data / waiting for it to fail.
    tfm = FOOOF(verbose=False)
    def raise_runtime_error(*args, **kwargs):
        raise FitError('Test-MonkeyPatch')
    tfm._fit_peaks = raise_runtime_error

    # Run a FOOOF fit - this should raise an error, but continue in try/except
    tfm.fit(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    # Check after failing out of fit, all results are reset
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfm, result)))

def test_fooof_debug():
    """Test FOOOF fit failure in debug mode."""

    tfm = FOOOF(verbose=False)
    tfm._maxfev = 5

    tfm.set_debug_mode(True)
    assert tfm._debug is True

    with raises(FitError):
        tfm.fit(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))
