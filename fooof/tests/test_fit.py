"""Tests for the FOOOF fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
    They serve rather as 'smoke tests', for if anything fails completely.
"""

from py.test import raises

import os
import numpy as np
import pkg_resources as pkg

from fooof import FOOOF
from fooof.synth import mk_fake_data
from fooof.utils import mk_freq_vector

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

    fm = FOOOF()
    fm.fit(xs, ys)

    # Check model results - background parameters
    assert np.all(np.isclose(bgp, fm.background_params_, [0.5, 0.1]))

    # Check model results - gaussian parameters
    for i, osc in enumerate(oscs):
        assert np.all(np.isclose(osc, fm._gaussian_params[i], [1.5, 0.25, 0.5]))

def test_fooof_fit_knee():
    """Test FOOOF fit, with a knee."""

    xs = mk_freq_vector([3, 50], 0.5)
    bgp = [50, 2, 1]
    oscs = [[10, 0.5, 2],
            [20, 0.3, 4]]

    xs, ys = mk_fake_data(xs, bgp, [it for osc in oscs for it in osc], True)

    fm = FOOOF(bg_use_knee=True)
    fm.fit(xs, ys)

    # Note: currently, this test has no accuracy checking at all
    assert True


def test_fooof_checks():
    """Test various checks, errors and edge cases in FOOOF."""

    xs, ys = mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2])

    fm = FOOOF()

    # Check dimension error
    with raises(ValueError):
        fm.fit(xs, np.reshape(ys, [1, len(ys)]))

    # Check shape mismatch error
    with raises(ValueError):
        fm.fit(xs[:-1], ys)

    # Check trim_psd range
    fm.fit(xs, ys, [3, 40])

    # Check freq of 0 issue
    xs, ys = mk_fake_data(mk_freq_vector([0, 50], 0.5), [50, 2], [10, 0.5, 2])
    fm.fit(xs, ys)

    # Check fit, plot and string report model error (no data / model fit)
    fm = FOOOF()
    with raises(ValueError):
        fm.fit()
    with raises(ValueError):
        fm.print_results()
    with raises(ValueError):
        fm.plot()

def test_fooof_load():
    """Test load into FOOOF. Note: loads files from test_core_io."""

    file_name_all = 'test_fooof_str_all'
    file_name_res = 'test_fooof_str_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    fm = FOOOF()

    fm.load(file_name_all, file_path)
    assert fm

    fm.load(file_name_res, file_path)
    assert fm

def test_fooof_prints_plot_get(tfm):
    """Test methods that print, plot, return results (alias and pass through methods).

    Checks: print_settings, print_results, plot, get_results.

    Note: minimal test - that methods run. No accuracy checking.
    """

    tfm.print_settings()
    tfm.print_results()
    tfm.print_report_issue()

    tfm.plot()

    out = tfm.get_results()
    assert out

def test_fooof_resets():
    """Check that all relevant data is cleared in the resest method."""

    fm = FOOOF()
    fm.fit(*mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    fm._reset_dat()
    fm._reset_settings()

    assert fm.freqs is None and fm.freq_range is None and fm.freq_res is None  \
        and fm.psd is None and fm.psd_fit_ is None and fm.background_params_ is None \
        and fm.oscillation_params_ is None and fm.r2_ is None and fm.error_ is None \
        and fm._psd_flat is None and fm._psd_osc_rm is None and fm._gaussian_params is None \
        and fm._background_fit is None and fm._oscillation_fit is None

def test_fooof_model():
    """Check that running the top level model method runs."""

    fm = FOOOF()

    fm.model(*mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4]))

    assert fm
