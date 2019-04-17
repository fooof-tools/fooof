"""Tests for fooof.fit, including the FOOOF object it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
    They serve rather as 'smoke tests', for if anything fails completely.
"""

from py.test import raises

import numpy as np
import pkg_resources as pkg

from fooof import FOOOF
from fooof.data import FOOOFSettings, FOOOFMetaData, FOOOFResults
from fooof.sim import gen_power_spectrum
from fooof.core.utils import group_three
from fooof.core.info import get_description

from fooof.tests.utils import get_tfm, plot_test

###################################################################################################
###################################################################################################

def test_fooof():
    """Check FOOOF object initializes properly."""

    assert FOOOF(verbose=False)

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

def test_fooof_fit_knee():
    """Test FOOOF fit, with a knee."""

    ap_params = [50, 2, 1]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum([3, 50], ap_params, gaussian_params)

    tfm = FOOOF(aperiodic_mode='knee', verbose=False)
    tfm.fit(xs, ys)

    # Note: currently, this test has no accuracy checking at all
    assert True


def test_fooof_checks():
    """Test various checks, errors and edge cases in FOOOF."""

    xs, ys = gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2])

    tfm = FOOOF(verbose=False)

    # Check dimension error
    with raises(ValueError):
        tfm.fit(xs, np.reshape(ys, [1, len(ys)]))

    # Check shape mismatch error
    with raises(ValueError):
        tfm.fit(xs[:-1], ys)

    # Check wrong data type error
    with raises(ValueError):
        tfm.fit(list(xs), list(ys))

    # Check trim_spectrum range
    tfm.fit(xs, ys, [3, 40])

    # Check freq of 0 issue
    xs, ys = gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2])
    tfm.fit(xs, ys)
    assert tfm.freqs[0] != 0

    # Check fit, and string report model error (no data / model fit)
    tfm = FOOOF(verbose=False)
    with raises(ValueError):
        tfm.fit()

def test_fooof_load():
    """Test load into FOOOF. Note: loads files from test_core_io."""

    file_name_all = 'test_fooof_str_all'
    file_name_res = 'test_fooof_str_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    tfm = FOOOF(verbose=False)

    tfm.load(file_name_all, file_path)
    assert tfm

    tfm.load(file_name_res, file_path)
    assert tfm

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
    for setting in get_description()['settings']:
        assert getattr(tfm, setting) == getattr(fooof_settings, setting)

    # Test adding meta data
    fooof_meta_data = FOOOFMetaData([3, 40], 0.5)
    tfm.add_meta_data(fooof_meta_data)
    for meta_dat in get_description()['meta_data']:
        assert getattr(tfm, meta_dat) == getattr(fooof_meta_data, meta_dat)

    # Test adding results
    fooof_results = FOOOFResults([1, 1], [10, 0.5, 0.5], 0.95, 0.02, [10, 0.5, 0.25])
    tfm.add_results(fooof_results)
    for setting in get_description()['results']:
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

    for dname in ['aperiodic_params', 'peak_params', 'error', 'r_squared', 'gaussian_params']:
        assert np.any(tfm.get_params(dname))

        if dname == 'aperiodic_params':
            for dtype in ['offset', 'exponent']:
                assert np.any(tfm.get_params(dname, dtype))

        if dname == 'peak_params':
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
    """Check that all relevant data is cleared in the resest method."""

    # Note: uses it's own tfm, to not clear the global one
    tfm = get_tfm()

    tfm._reset_data_results()
    tfm._reset_internal_settings()

    desc = get_description()

    for data in ['data', 'results', 'model_components']:
        for field in desc[data]:
            assert getattr(tfm, field) == None
    assert tfm.freqs == None and tfm.fooofed_spectrum_ == None

def test_fooof_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    tfm = FOOOF(verbose=False)

    tfm.report(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    assert tfm

def test_fooof_fit_failure():
    """Test that fit handles a failure."""

    # Use a new FOOOF, that is monkey-patched to raise an error
    #  This mimicks the main fit-failure, without requiring bad data / waiting for it to fail.
    tfm = FOOOF(verbose=False)
    def raise_runtime_error(*args, **kwargs):
        raise RuntimeError('Test-MonkeyPatch')
    tfm._fit_peaks = raise_runtime_error

    # Run a FOOOF fit - this should raise an error, but continue in try/except
    tfm.fit(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    # Check after failing out of fit, all results are reset
    for result in get_description()['results']:
        cur_res = getattr(tfm, result)
        assert cur_res is None or np.all(np.isnan(cur_res))
