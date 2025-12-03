"""Tests for specparam.models.model, including the model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np
from pytest import raises

from specparam.utils.select import groupby
from specparam.modutils.errors import FitError
from specparam.metrics.definitions import METRICS
from specparam.sim import gen_freqs, sim_power_spectrum
from specparam.modes.definitions import AP_MODES, PE_MODES
from specparam.models.utils import compare_model_objs
from specparam.modutils.dependencies import safe_import
from specparam.modutils.errors import DataError, NoDataError, InconsistentDataError

pd = safe_import('pandas')

from specparam.tests.tsettings import TEST_DATA_PATH
from specparam.tests.tdata import default_spectrum_params, get_tfm
from specparam.tests.tutils import plot_test

from specparam.models.model import *

###################################################################################################
###################################################################################################

def test_model_object():
    """Check model object initializes properly."""

    assert SpectralModel()

    # Check initialization across all possibile mode combinations
    for ap_mode in AP_MODES:
        for pe_mode in PE_MODES:
            assert SpectralModel(aperiodic_mode=ap_mode, periodic_mode=pe_mode, verbose=False)

def test_has_data(tfm):
    """Test the has_data property attribute, with and without model fits."""

    assert tfm.data.has_data

    ntfm = SpectralModel()
    assert not ntfm.data.has_data

def test_has_model(tfm):
    """Test the has_model property attribute, with and without model fits."""

    assert tfm.results.has_model

    ntfm = SpectralModel()
    assert not ntfm.results.has_model

def test_n_properties(tfm):

    assert tfm.results.n_peaks
    assert tfm.results.n_params

def test_fit_nk():
    """Test fit, no knee."""

    ap_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]
    nlv = 0.0025
    xs, ys = sim_power_spectrum([3, 50], {'fixed' : ap_params}, {'gaussian' : gauss_params}, nlv)

    tfm = SpectralModel(verbose=False)
    tfm.fit(xs, ys)

    # Check model results - aperiodic parameters
    assert np.allclose(ap_params, tfm.results.params.aperiodic.params, [0.5, 0.1])

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(groupby(gauss_params, 3)):
        assert np.allclose(gauss, \
            tfm.results.params.periodic.get_params('fit')[ii], [2.0, 0.5, 1.0])

def test_fit_nk_noise():
    """Test fit on noisy data, to make sure nothing breaks."""

    nlv = 1.0
    xs, ys = sim_power_spectrum(*default_spectrum_params(), nlv=nlv)

    tfm = SpectralModel(max_n_peaks=8, verbose=False)
    tfm.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfm.results.has_model

def test_fit_knee():
    """Test fit, with a knee."""

    ap_params = [50, 10, 1]
    gauss_params = [10, 0.3, 2, 20, 0.1, 4, 60, 0.3, 1]
    nlv = 0.0025

    xs, ys = sim_power_spectrum([1, 150], {'knee' : ap_params}, {'gaussian' : gauss_params}, nlv)

    tfm = SpectralModel(aperiodic_mode='knee', verbose=False)
    tfm.fit(xs, ys)

    # Check model results - aperiodic parameters
    assert np.allclose(ap_params, tfm.results.params.aperiodic.params, [1, 2, 0.2])

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(groupby(gauss_params, 3)):
        assert np.allclose(gauss, \
            tfm.results.params.periodic.get_params('fit')[ii], [2.0, 0.5, 1.0])

def test_fit_default_metrics():
    """Test computing metrics, post model fitting."""

    tfm = SpectralModel(verbose=False)

    # Hack fake data with known properties: total error magnitude 2
    tfm.data.power_spectrum = np.array([1, 2, 3, 4, 5])
    tfm.results.model.modeled_spectrum = np.array([1, 2, 5, 4, 5])

    # Check default metrics
    tfm.results.metrics.compute_metrics(tfm.data, tfm.results)
    assert np.isclose(tfm.results.metrics.results['error_mae'], 0.4)
    assert np.isclose(tfm.results.metrics.results['gof_rsquared'], 0.75757575)

def test_fit_custom_metrics():

    metrics = list(METRICS.keys())
    tfm = SpectralModel(metrics=metrics)

    ap_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]
    nlv = 0.0025
    xs, ys = sim_power_spectrum([3, 50], {'fixed' : ap_params}, {'gaussian' : gauss_params}, nlv)

    tfm.fit(xs, ys)
    for key, val in tfm.results.metrics.results.items():
        assert key in metrics
        assert isinstance(val, float)

def test_fit_null_conversions(tfm):

    null_converters = tfm.modes.get_params('dict')
    ntfm = SpectralModel(converters=null_converters)

    ntfm.fit(tfm.data.freqs, tfm.get_data('full', 'linear'))
    assert np.all(np.isnan(ntfm.results.get_params('aperiodic', version='converted')))
    assert np.all(np.isnan(ntfm.results.get_params('periodic', version='converted')))

def test_fit_custom_conversions(tfm):

    converters = {'periodic' : {'pw' : 'lin_sub'}}
    ntfm = SpectralModel(converters=converters)

    ntfm.fit(tfm.data.freqs, tfm.get_data('full', 'linear'))
    assert not np.array_equal(
        tfm.results.get_params('periodic', 'pw'), ntfm.results.get_params('periodic', 'pw'))

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
    assert tfm.data.freqs[0] != 0

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

def test_load(tfm):
    """Test loading data into model object.
    Note: loads files from test_save_model in specparam/tests/io/test_models.py."""

    # Test loading just results
    ntfm = SpectralModel(verbose=False)
    ntfm.load('test_model_res', TEST_DATA_PATH)

    # Check that result attributes get filled
    for component in tfm.modes.components:
        assert getattr(ntfm.results.params, component).has_params

    # Test that settings and data are None
    for setting in tfm.algorithm.settings.names:
        assert getattr(ntfm.algorithm.settings, setting) is None
    assert ntfm.data.power_spectrum is None

    # Test loading just settings
    ntfm = SpectralModel(verbose=False)
    ntfm.load('test_model_set', TEST_DATA_PATH)
    assert tfm.algorithm.settings.values == ntfm.algorithm.settings.values
    # Test that results and data are None
    for component in tfm.modes.components:
        assert not getattr(ntfm.results.params, component).has_params
    assert ntfm.data.power_spectrum is None

    # Test loading just data
    ntfm = SpectralModel(verbose=False)
    ntfm.load('test_model_dat', TEST_DATA_PATH)
    assert ntfm.data.has_data
    assert np.array_equal(tfm.data.power_spectrum, ntfm.data.power_spectrum)
    # Test that settings and results are None
    for setting in tfm.algorithm.settings.names:
        assert getattr(ntfm.algorithm.settings, setting) is None
    for component in tfm.modes.components:
        assert not getattr(ntfm.results.params, component).has_params

    # Test loading all elements
    ntfm = SpectralModel(verbose=False)
    ntfm.load('test_model_all', TEST_DATA_PATH)
    assert compare_model_objs([tfm, ntfm], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])
    for data in tfm.data._fields:
        assert np.array_equal(getattr(tfm.data, data), getattr(ntfm.data, data))
    for component in tfm.modes.components:
        assert getattr(ntfm.results.params, component).has_params

def test_add_data(tresults):
    """Tests method to add data to model objects."""

    # This test uses it's own model object, to not add stuff to the global one
    tfm = get_tfm()

    # Test data for adding
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])

    # Test adding data
    tfm.add_data(freqs, pows)
    assert tfm.data.has_data
    assert np.all(tfm.data.freqs == freqs)
    assert np.all(tfm.data.power_spectrum == np.log10(pows))

    # Test that prior data does not get cleared, when requesting not to clear
    tfm._reset_data_results(True, True, True)
    tfm.results.add_results(tresults)
    tfm.add_data(freqs, pows, clear_results=False)
    assert tfm.data.has_data
    assert tfm.results.has_model

    # Test that prior data does get cleared, when requesting not to clear
    tfm._reset_data_results(True, True, True)
    tfm.add_data(freqs, pows, clear_results=True)
    assert tfm.data.has_data
    assert not tfm.results.has_model

def test_get_params(tfm):
    """Test the get_params method."""

    for component in tfm.modes.components:
        assert np.any(tfm.get_params(component))
        for pname in getattr(tfm.modes, component).params.labels:
            assert np.any(tfm.get_params(component, pname))

def test_get_data(tfm):

    for comp in ['full', 'aperiodic', 'peak']:
        for space in ['log', 'linear']:
            assert isinstance(tfm.get_data(comp, space), np.ndarray)

def test_get_component(tfm):

    for comp in ['full', 'aperiodic', 'peak']:
        for space in ['log', 'linear']:
            assert isinstance(tfm.results.model.get_component(comp, space), np.ndarray)

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
    for field in tfm.data._fields:
        assert getattr(tfm.data, field) is None
    for key, value in tfm.results.model.__dict__.items():
        assert value is None
    for component in tfm.modes.components:
        assert not getattr(tfm.results.params, component).has_params
    assert tfm.data.freqs is None and tfm.results.model.modeled_spectrum is None

def test_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    tfm = SpectralModel(verbose=False)
    tfm.report(*sim_power_spectrum(*default_spectrum_params()))

    assert tfm

def test_fit_failure():
    """Test model fit failures."""

    ## Induce a runtime error, and check it runs through
    tfm = SpectralModel(verbose=False)
    tfm.algorithm._cf_settings.maxfev = 2

    tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

    # Check after failing out of fit, all results are reset
    for component in tfm.modes.components:
        assert not getattr(tfm.results.params, component).has_params

    ## Monkey patch to check errors in general
    #  This mimics the main fit-failure, without requiring bad data / waiting for it to fail.
    tfm = SpectralModel(verbose=False)
    def raise_runtime_error(*args, **kwargs):
        raise FitError('Test-MonkeyPatch')
    tfm.algorithm._fit_peaks = raise_runtime_error

    # Run a model fit - this should raise an error, but continue in try/except
    tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

    # Check after failing out of fit, all results are reset
    for component in tfm.modes.components:
        assert not getattr(tfm.results.params, component).has_params

def test_debug():
    """Test model object in debug state, including with fit failures."""

    tfm = SpectralModel(verbose=False)
    tfm.algorithm._cf_settings.maxfev = 2

    tfm.algorithm.set_debug(True)
    assert tfm.algorithm._debug is True

    with raises(FitError):
        tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

def test_set_checks():
    """Test changing checks using set_checks, and that checks get turned off.
    Note that testing for checks raising errors happens in test_checks.`"""

    tfm = SpectralModel(verbose=False)
    tfm.data.set_checks(False, False)

    # Add bad frequency data, with check freqs turned off
    freqs = np.array([1, 2, 4])
    powers = np.array([1, 2, 3])
    tfm.add_data(freqs, powers)
    assert tfm.data.has_data

    # Add bad power values data, with check data turned off
    freqs = gen_freqs([3, 30], 1)
    powers = np.ones_like(freqs) * np.nan
    tfm.add_data(freqs, powers)
    assert tfm.data.has_data

    # Model fitting should execute, but return a null model fit, given the NaNs, without failing
    tfm.fit()
    assert not tfm.results.has_model

    # Reset checks to true
    tfm.data.set_checks(True, True)
    assert tfm.data.checks['freqs'] is True
    assert tfm.data.checks['data'] is True

def test_to_df(tfm, tbands, skip_if_no_pandas):

    df1 = tfm.to_df(2)
    assert isinstance(df1, pd.Series)
    df2 = tfm.to_df(tbands)
    assert isinstance(df2, pd.Series)
