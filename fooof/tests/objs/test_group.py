"""Tests for the fooof.objs.group, including the FOOOFGroup object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np
from numpy.testing import assert_equal

from fooof.data import FOOOFResults
from fooof.core.items import OBJ_DESC
from fooof.sim import gen_group_power_spectra

from fooof.tests.settings import TEST_DATA_PATH
from fooof.tests.tutils import default_group_params, plot_test

from fooof.objs.group import *

###################################################################################################
###################################################################################################

def test_fg():
    """Check FOOOFGroup object initializes properly."""

    # Note: doesn't assert fg itself, as it return false when group_results are empty
    #  This is due to the __len__ used in FOOOFGroup
    fg = FOOOFGroup(verbose=False)
    assert isinstance(fg, FOOOFGroup)

def test_fg_iter(tfg):
    """Check iterating through FOOOFGroup."""

    for res in tfg:
        assert res

def test_fg_getitem(tfg):
    """Check indexing, from custom __getitem__, in FOOOFGroup."""

    assert tfg[0]

def test_fg_has_data(tfg):
    """Test the has_data property attribute, with and without data."""

    assert tfg.has_model

    ntfg = FOOOFGroup()
    assert not ntfg.has_data

def test_fg_has_model(tfg):
    """Test the has_model property attribute, with and without model fits."""

    assert tfg.has_model

    ntfg = FOOOFGroup()
    assert not ntfg.has_model

def test_fooof_n_peaks(tfg):
    """Test the n_peaks property attribute."""

    assert tfg.n_peaks_

def test_n_null(tfg):
    """Test the n_null_ property attribute."""

    # Since there should have been no failed fits, this should return 0
    assert tfg.n_null_ == 0

def test_null_inds(tfg):
    """Test the null_inds_ property attribute."""

    # Since there should be no failed fits, this should return an empty list
    assert tfg.null_inds_ == []

def test_fg_fit_nk():
    """Test FOOOFGroup fit, no knee."""

    n_spectra = 2
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params(), nlvs=0)

    tfg = FOOOFGroup(verbose=False)
    tfg.fit(xs, ys)
    out = tfg.get_results()

    assert out
    assert len(out) == n_spectra
    assert isinstance(out[0], FOOOFResults)
    assert np.all(out[1].aperiodic_params)

def test_fg_fit_nk_noise():
    """Test FOOOFGroup fit, no knee, on noisy data, to make sure nothing breaks."""

    n_spectra = 5
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params(), nlvs=1.0)

    tfg = FOOOFGroup(max_n_peaks=8, verbose=False)
    tfg.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfg.has_model

def test_fg_fit_knee():
    """Test FOOOFGroup fit, with a knee."""

    n_spectra = 2
    ap_params = [50, 2, 1]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_group_power_spectra(n_spectra, [1, 150], ap_params, gaussian_params, nlvs=0)

    tfg = FOOOFGroup(aperiodic_mode='knee', verbose=False)
    tfg.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfg.has_model

def test_fg_fit_progress(tfg):
    """Test running FOOOFGroup fitting, with a progress bar."""

    tfg.fit(progress='tqdm')

def test_fg_fail():
    """Test FOOOFGroup fit, in a way that some fits will fail.
    Also checks that model failures don't cause errors.
    """

    # Create some noisy spectra that will be hard to fit
    fs, ps = gen_group_power_spectra(10, [3, 6], [1, 1], [10, 1, 1], nlvs=10)

    # Use a fg with the max iterations set so low that it will fail to converge
    ntfg = FOOOFGroup()
    ntfg._maxfev = 5

    # Fit models, where some will fail, to see if it completes cleanly
    ntfg.fit(fs, ps)

    # Check that results are all
    for res in ntfg.get_results():
        assert res

    # Test that get_params works with failed model fits
    outs1 = ntfg.get_params('aperiodic_params')
    outs2 = ntfg.get_params('aperiodic_params', 'exponent')
    outs3 = ntfg.get_params('peak_params')
    outs4 = ntfg.get_params('peak_params', 0)
    outs5 = ntfg.get_params('gaussian_params', 2)

    # Test shortcut labels
    outs6 = ntfg.get_params('aperiodic')
    outs6 = ntfg.get_params('peak', 'CF')

    # Test the property attributes related to null model fits
    #   This checks that they do the right thing when there are null fits (failed fits)
    assert ntfg.n_null_ > 0
    assert ntfg.null_inds_

def test_fg_drop():
    """Test function to drop results from FOOOFGroup."""

    n_spectra = 3
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup(verbose=False)

    # Test dropping one ind
    tfg.fit(xs, ys)
    tfg.drop(0)

    dropped_fres = tfg.group_results[0]
    for field in dropped_fres._fields:
        assert np.all(np.isnan(getattr(dropped_fres, field)))

    # Test dropping multiple inds
    tfg.fit(xs, ys)
    drop_inds = [0, 2]
    tfg.drop(drop_inds)

    for drop_ind in drop_inds:
        dropped_fres = tfg.group_results[drop_ind]
        for field in dropped_fres._fields:
            assert np.all(np.isnan(getattr(dropped_fres, field)))

    # Test that a FOOOFGroup that has had inds dropped still works with `get_params`
    cfs = tfg.get_params('peak_params', 1)
    exps = tfg.get_params('aperiodic_params', 'exponent')
    assert np.all(np.isnan(exps[drop_inds]))
    assert np.all(np.invert(np.isnan(np.delete(exps, drop_inds))))

def test_fg_fit_par():
    """Test FOOOFGroup fit, running in parallel."""

    n_spectra = 2
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup(verbose=False)
    tfg.fit(xs, ys, n_jobs=2)
    out = tfg.get_results()

    assert out
    assert len(out) == n_spectra
    assert isinstance(out[0], FOOOFResults)
    assert np.all(out[1].aperiodic_params)

def test_fg_print(tfg):
    """Check print method (alias)."""

    tfg.print_results()
    assert True

def test_get_results(tfg):
    """Check get results method."""

    assert tfg.get_results()

def test_get_params(tfg):
    """Check get_params method."""

    for dname in ['aperiodic_params', 'peak_params', 'error', 'r_squared', 'gaussian_params']:
        assert np.any(tfg.get_params(dname))

        if dname == 'aperiodic_params':
            for dtype in ['offset', 'exponent']:
                assert np.any(tfg.get_params(dname, dtype))

        if dname == 'peak_params':
            for dtype in ['CF', 'PW', 'BW']:
                assert np.any(tfg.get_params(dname, dtype))

@plot_test
def test_fg_plot(tfg, skip_if_no_mpl):
    """Check alias method for plot."""

    tfg.plot()

def test_fg_load():
    """Test load into FOOOFGroup. Note: loads files from test_core_io."""

    file_name_res = 'test_fooofgroup_res'
    file_name_set = 'test_fooofgroup_set'
    file_name_dat = 'test_fooofgroup_dat'

    # Test loading just results
    tfg = FOOOFGroup(verbose=False)
    tfg.load(file_name_res, TEST_DATA_PATH)
    assert len(tfg.group_results) > 0
    # Test that settings and data are None
    #   Except for aperiodic mode, which can be inferred from the data
    for setting in OBJ_DESC['settings']:
        if setting is not 'aperiodic_mode':
            assert getattr(tfg, setting) is None
    assert tfg.power_spectra is None

    # Test loading just settings
    tfg = FOOOFGroup(verbose=False)
    tfg.load(file_name_set, TEST_DATA_PATH)
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) is not None
    # Test that results and data are None
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfg, result)))
    assert tfg.power_spectra is None

    # Test loading just data
    tfg = FOOOFGroup(verbose=False)
    tfg.load(file_name_dat, TEST_DATA_PATH)
    assert tfg.power_spectra is not None
    # Test that settings and results are None
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) is None
    for result in OBJ_DESC['results']:
        assert np.all(np.isnan(getattr(tfg, result)))

    # Test loading all elements
    tfg = FOOOFGroup(verbose=False)
    file_name_all = 'test_fooofgroup_all'
    tfg.load(file_name_all, TEST_DATA_PATH)
    assert len(tfg.group_results) > 0
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) is not None
    assert tfg.power_spectra is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfg, meta_dat) is not None

def test_fg_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    n_spectra = 2
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup(verbose=False)
    tfg.report(xs, ys)

    assert tfg

def test_fg_get_fooof(tfg):
    """Check return of an individual model fit to a FOOOF object from FOOOFGroup."""

    # Check without regenerating
    tfm0 = tfg.get_fooof(0, False)
    assert tfm0
    # Check that settings are copied over properly
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) == getattr(tfm0, setting)

    # Check with regenerating
    tfm1 = tfg.get_fooof(1, True)
    assert tfm1
    # Check that regenerated model is created
    for result in OBJ_DESC['results']:
        assert np.all(getattr(tfm1, result))

    # Test when object has no data (clear a copy of tfg)
    new_tfg = tfg.copy()
    new_tfg._reset_data_results(False, True, True, True)
    tfm2 = new_tfg.get_fooof(0, True)
    assert tfm2
    # Check that data info is copied over properly
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm2, meta_dat)

def test_fg_get_group(tfg):
    """Check the return of a sub-sampled FOOOFGroup."""

    # Check with list index
    inds1 = [1, 2]
    nfg1 = tfg.get_group(inds1)
    assert isinstance(nfg1, FOOOFGroup)

    # Check with range index
    inds2 = range(0, 2)
    nfg2 = tfg.get_group(inds2)
    assert isinstance(nfg2, FOOOFGroup)

    # Check that settings are copied over properly
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) == getattr(nfg1, setting)
        assert getattr(tfg, setting) == getattr(nfg2, setting)

    # Check that data info is copied over properly
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(nfg1, meta_dat)
        assert getattr(nfg2, meta_dat)

    # Check that the correct data is extracted
    assert_equal(tfg.power_spectra[inds1, :], nfg1.power_spectra)
    assert_equal(tfg.power_spectra[inds2, :], nfg2.power_spectra)

    # Check that the correct results are extracted
    assert [tfg.group_results[ind] for ind in inds1] == nfg1.group_results
    assert [tfg.group_results[ind] for ind in inds2] == nfg2.group_results
