"""Tests for the FOOOF fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
    They serve rather as 'smoke tests', for if anything fails completely.
"""

from py.test import raises

import numpy as np
import pkg_resources as pkg

from fooof import FOOOF
from fooof.synth import gen_power_spectrum
from fooof.core.modutils import get_obj_desc
from fooof.core.utils import group_three

from fooof.tests.utils import get_tfm, plot_test

###################################################################################################
###################################################################################################

def test_fooof():
    """Check FOOOF object initializes properly."""

    assert FOOOF()

def test_fooof_fit_nk():
    """Test FOOOF fit, no knee."""

    bgp = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum([3, 50], bgp, gauss_params)

    tfm = FOOOF()
    tfm.fit(xs, ys)

    # Check model results - background parameters
    assert np.all(np.isclose(bgp, tfm.background_params_, [0.5, 0.1]))

    # Check model results - gaussian parameters
    for ii, gauss in enumerate(group_three(gauss_params)):
        assert np.all(np.isclose(gauss, tfm._gaussian_params[ii], [1.5, 0.25, 0.5]))

def test_fooof_fit_knee():
    """Test FOOOF fit, with a knee."""

    bgp = [50, 2, 1]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum([3, 50], bgp, gauss_params)

    tfm = FOOOF(background_mode='knee')
    tfm.fit(xs, ys)

    # Note: currently, this test has no accuracy checking at all
    assert True


def test_fooof_checks():
    """Test various checks, errors and edge cases in FOOOF."""

    xs, ys = gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2])

    tfm = FOOOF()

    # Check dimension error
    with raises(ValueError):
        tfm.fit(xs, np.reshape(ys, [1, len(ys)]))

    # Check shape mismatch error
    with raises(ValueError):
        tfm.fit(xs[:-1], ys)

    # Check trim_spectrum range
    tfm.fit(xs, ys, [3, 40])

    # Check freq of 0 issue
    xs, ys = gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2])
    tfm.fit(xs, ys)
    assert tfm.freqs[0] != 0

    # Check fit, and string report model error (no data / model fit)
    tfm = FOOOF()
    with raises(ValueError):
        tfm.fit()

def test_fooof_load():
    """Test load into FOOOF. Note: loads files from test_core_io."""

    file_name_all = 'test_fooof_str_all'
    file_name_res = 'test_fooof_str_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    tfm = FOOOF()

    tfm.load(file_name_all, file_path)
    assert tfm

    tfm.load(file_name_res, file_path)
    assert tfm

def test_copy():
    """Test copy FOOOF method."""

    tfm = FOOOF()
    ntfm = tfm.copy()

    assert tfm != ntfm

def test_fooof_prints_get(tfm):
    """Test methods that print, return results (alias and pass through methods).

    Checks: print_settings, print_results, get_results."""

    tfm.print_settings()
    tfm.print_results()
    tfm.print_report_issue()

    out = tfm.get_results()
    assert out

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

    assert tfm.freqs is None and tfm.freq_range is None and tfm.freq_res is None  \
        and tfm.power_spectrum is None and tfm.fooofed_spectrum_ is None and tfm._spectrum_flat is None \
        and tfm._spectrum_peak_rm is None and tfm._bg_fit is None and tfm._peak_fit is None

    assert np.all(np.isnan(tfm.background_params_)) and np.all(np.isnan(tfm.peak_params_)) \
        and np.all(np.isnan(tfm.r_squared_)) and np.all(np.isnan(tfm.error_)) and np.all(np.isnan(tfm._gaussian_params))

def test_fooof_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    tfm = FOOOF()

    tfm.report(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    assert tfm

def test_fooof_fit_failure():
    """Test that fit handles a failure."""

    # Use a new FOOOF, that is monkey-patched to raise an error
    #  This mimicks the main fit-failure, without requiring bad data / waiting for it to fail.
    tfm = FOOOF()
    def raise_runtime_error(*args, **kwargs):
        raise RuntimeError('Test-MonkeyPatch')
    tfm._fit_peaks = raise_runtime_error

    # Run a FOOOF fit - this should raise an error, but continue in try/except
    tfm.fit(*gen_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    # Check after failing out of fit, all results are reset
    for result in get_obj_desc()['results']:
        cur_res = getattr(tfm, result)
        assert cur_res is None or np.all(np.isnan(cur_res))
