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
from fooof.synth import mk_fake_data
from fooof.utils import mk_freq_vector

from fooof.tests.utils import get_tfm

###################################################################################################
###################################################################################################

def test_fooof():
    """Check FOOOF object initializes properly."""

    assert FOOOF()

def test_fooof_fit_nk():
    """Test FOOOF fit, no knee."""

    xs = mk_freq_vector([3, 50], 0.5)
    bgp = [50, 2]
    oscs = [[10, 0.5, 2],
            [20, 0.3, 4]]

    xs, ys = mk_fake_data(xs, bgp, [it for osc in oscs for it in osc])

    tfm = FOOOF()
    tfm.fit(xs, ys)

    # Check model results - background parameters
    assert np.all(np.isclose(bgp, tfm.background_params_, [0.5, 0.1]))

    # Check model results - gaussian parameters
    for i, osc in enumerate(oscs):
        assert np.all(np.isclose(osc, tfm._gaussian_params[i], [1.5, 0.25, 0.5]))

def test_fooof_fit_knee():
    """Test FOOOF fit, with a knee."""

    xs = mk_freq_vector([3, 50], 0.5)
    bgp = [50, 2, 1]
    oscs = [[10, 0.5, 2],
            [20, 0.3, 4]]

    xs, ys = mk_fake_data(xs, bgp, [it for osc in oscs for it in osc], True)

    tfm = FOOOF(bg_use_knee=True)
    tfm.fit(xs, ys)

    # Note: currently, this test has no accuracy checking at all
    assert True


def test_fooof_checks():
    """Test various checks, errors and edge cases in FOOOF."""

    xs, ys = mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2])

    tfm = FOOOF()

    # Check dimension error
    with raises(ValueError):
        tfm.fit(xs, np.reshape(ys, [1, len(ys)]))

    # Check shape mismatch error
    with raises(ValueError):
        tfm.fit(xs[:-1], ys)

    # Check trim_psd range
    tfm.fit(xs, ys, [3, 40])

    # Check freq of 0 issue
    xs, ys = mk_fake_data(mk_freq_vector([0, 50], 0.5), [50, 2], [10, 0.5, 2])
    tfm.fit(xs, ys)
    assert tfm.freqs[0] != 0

    # Check fit, plot and string report model error (no data / model fit)
    tfm = FOOOF()
    with raises(ValueError):
        tfm.fit()
    with raises(ValueError):
        tfm.print_results()
    with raises(ValueError):
        tfm.plot()

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

def test_fooof_prints_plot_get(tfm):
    """Test methods that print, plot, return results (alias and pass through methods).

    Checks: print_settings, print_results, plot, get_results."""

    tfm.print_settings()
    tfm.print_results()
    tfm.print_report_issue()

    tfm.plot()

    out = tfm.get_results()
    assert out

def test_fooof_resets():
    """Check that all relevant data is cleared in the resest method."""

    # Note: uses it's own tfm, to not clear the global one
    tfm = get_tfm()

    tfm._reset_dat()
    tfm._reset_settings()

    assert tfm.freqs is None and tfm.freq_range is None and tfm.freq_res is None  \
        and tfm.psd is None and tfm.psd_fit_ is None and tfm.background_params_ is None \
        and tfm.oscillation_params_ is None and tfm.r2_ is None and tfm.error_ is None \
        and tfm._psd_flat is None and tfm._psd_osc_rm is None and tfm._gaussian_params is None \
        and tfm._background_fit is None and tfm._oscillation_fit is None

def test_fooof_model():
    """Check that running the top level model method runs."""

    tfm = FOOOF()

    tfm.model(*mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    assert tfm
