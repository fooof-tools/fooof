"""Tests for the FOOOFGroup fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
    They serve rather as 'smoke tests', for if anything fails completely.
"""

import pkg_resources as pkg

import numpy as np

from fooof import FOOOFGroup, fit_fooof_group_3d
from fooof.fit import FOOOFResult
from fooof.synth import gen_group_power_spectra
from fooof.core.modutils import get_obj_desc

from fooof.tests.utils import default_group_params, plot_test

###################################################################################################
###################################################################################################

def test_fg():
    """Check FOOOFGroup object initializes properly."""

    # Note: doesn't assert fg itself, as it return false when group_results are empty
    #  This is due to the __len__ used in FOOOFGroup
    fg = FOOOFGroup()
    assert True

def test_fg_iter(tfg):
    """Check iterating through FOOOFGroup."""

    for res in tfg:
        assert res

def test_fg_getitem(tfg):
    """Check indexing, from custom __getitem__, in FOOOFGroup."""

    assert tfg[0]

def test_fg_fit():
    """Test FOOOFGroup fit, no knee."""

    n_spectra = 2
    xs, ys, _ = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup()
    tfg.fit(xs, ys)
    out = tfg.get_results()

    assert out
    assert len(out) == n_spectra
    assert isinstance(out[0], FOOOFResult)
    assert np.all(out[1].background_params)

def test_fg_fit_par():
    """Test FOOOFGroup fit, running in parallel."""

    n_spectra = 2
    xs, ys, _ = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup()
    tfg.fit(xs, ys, n_jobs=2)
    out = tfg.get_results()

    assert out
    assert len(out) == n_spectra
    assert isinstance(out[0], FOOOFResult)
    assert np.all(out[1].background_params)

def test_fg_print(tfg):
    """Check print method (alias)."""

    tfg.print_results()
    assert True

def test_get_results(tfg):
    """Check get results method."""

    assert tfg.get_results()

def test_get_all_data(tfg):
    """Check get_all_data method."""

    for dname in ['background_params', 'peak_params', 'error', 'r_squared', 'gaussian_params']:
        assert np.any(tfg.get_all_data(dname))

        if dname == 'background_params':
            for dtype in ['intercept', 'slope']:
                assert np.any(tfg.get_all_data(dname, dtype))

        if dname == 'peak_params':
            for dtype in ['CF', 'Amp', 'BW']:
                assert np.any(tfg.get_all_data(dname, dtype))

@plot_test
def test_fg_plot(tfg, skip_if_no_mpl):
    """Check alias method for plot."""

    tfg.plot()

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

    n_spectra = 2
    xs, ys, _ = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup()
    tfg.report(xs, ys)

    assert tfg

def test_fg_get_fooof(tfg):
    """Check return of an individual model fit to a FOOOF object from FOOOFGroup."""

    desc = get_obj_desc()

    # Check without regenerating
    tfm0 = tfg.get_fooof(0, False)
    assert tfm0
    # Check that settings are copied over properly
    for setting in desc['settings']:
        assert getattr(tfg, setting) == getattr(tfm0, setting)

    # Check with regenerating
    tfm1 = tfg.get_fooof(1, True)
    assert tfm1
    # Check that regenerated model is created
    for result in desc['results']:
        assert np.all(getattr(tfm1, result))

def test_fit_fooof_group_3d(tfg):
    """   """

    n_spectra = 2
    xs, ys, _ = gen_group_power_spectra(n_spectra, *default_group_params())
    ys = np.stack([ys, ys], axis=0)

    tfg = FOOOFGroup()
    fgs = fit_fooof_group_3d(tfg, xs, ys)

    assert len(fgs) == 2
    for fg in fgs:
        assert fg
