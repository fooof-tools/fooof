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
from fooof.synth import mk_fake_group_data
from fooof.utils import mk_freq_vector

##########################################################################################
##########################################################################################

def test_fg():
    """Check FOOOFGroup object initializes properly."""

    assert FOOOFGroup()

def test_fg_iter(tfg):
    """Check iterating through FOOOFGroup."""

    for res in tfg:
        assert res

def test_fg_fit():
    """Test FOOOFGroup fit, no knee."""

    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), n_psds=2)

    fg = FOOOFGroup()
    fg.fit(xs, ys)
    out = fg.get_results()

    assert out

def test_fg_fit_par():
    """Test FOOOFGroup fit, running in parallel."""

    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), n_psds=2)

    fg = FOOOFGroup()
    fg.fit(xs, ys, n_jobs=2)
    out = fg.get_results()

    assert out

def test_fg_plot_get(tfg):
    """Check methods that print, plot, and create report."""

    tfg.print_results()
    tfg.plot()

    assert True

def test_fg_load():
    """Test load into FOOOFGroup. Note: loads files from test_core_io."""

    set_file_name = 'test_fooof_group_set'
    res_file_name = 'test_fooof_group_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    nfg = FOOOFGroup()

    nfg.load(set_file_name, file_path)
    assert nfg

    nfg.load(res_file_name, file_path)
    assert nfg

def test_fg_model():
    """Check that running the top level model method runs."""

    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), n_psds=2)

    fg = FOOOFGroup()
    fg.model(xs, ys)

    assert fg

def test_fg_get_fooof(tfg):
    """Check return of an individual PSD in a FOOOF object from FOOOFGroup."""

    fm0 = tfg.get_fooof(0, False)
    assert fm0

    fm1 = tfg.get_fooof(1, True)
    assert fm1
