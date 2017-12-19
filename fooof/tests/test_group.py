"""Tests for the FOOOFGroup fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
    They serve rather as 'smoke tests', for if anything fails completely.
"""

import os
import pkg_resources as pkg

import numpy as np

from fooof import FOOOFGroup
from fooof.fit import FOOOFResult
from fooof.synth import mk_fake_group_data
from fooof.utils import mk_freq_vector

###################################################################################################
###################################################################################################

def test_fg():
    """Check FOOOFGroup object initializes properly."""

    fg = FOOOFGroup()
    assert True

def test_fg_iter(tfg):
    """Check iterating through FOOOFGroup."""

    for res in tfg:
        assert res

def test_fg_fit():
    """Test FOOOFGroup fit, no knee."""

    n_psds = 2
    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), n_psds=n_psds)

    tfg = FOOOFGroup()
    tfg.fit(xs, ys)
    out = tfg.get_results()

    assert out
    assert len(out) == n_psds
    assert isinstance(out[0], FOOOFResult)
    assert np.all(out[1].background_params)

def test_fg_fit_par():
    """Test FOOOFGroup fit, running in parallel."""

    n_psds = 2
    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), n_psds=n_psds)

    tfg = FOOOFGroup()
    tfg.fit(xs, ys, n_jobs=2)
    out = tfg.get_results()

    assert out
    assert len(out) == n_psds
    assert isinstance(out[0], FOOOFResult)
    assert np.all(out[1].background_params)

def test_fg_print_get(tfg):
    """Check methods that print, plot."""

    tfg.print_results()
    out = tfg.get_results()

    assert True

def test_fg_plot(tfg, skip_if_no_mpl):
    """Check alias method for plot."""

    tfg.plot()

    assert True

def test_fg_load():
    """Test load into FOOOFGroup. Note: loads files from test_core_io."""

    set_file_name = 'test_fooof_group_set'
    res_file_name = 'test_fooof_group_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    tfg = FOOOFGroup()

    tfg.load(set_file_name, file_path)
    assert tfg

    tfg.load(res_file_name, file_path)
    assert tfg

def test_fg_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), n_psds=2)

    tfg = FOOOFGroup()
    tfg.report(xs, ys)

    assert tfg

def test_fg_get_fooof(tfg):
    """Check return of an individual PSD in a FOOOF object from FOOOFGroup."""

    tfm0 = tfg.get_fooof(0, False)
    assert tfm0

    tfm1 = tfg.get_fooof(1, True)
    assert tfm1
