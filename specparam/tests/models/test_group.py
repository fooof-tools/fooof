"""Tests for the specparam.models.group, including the group model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import os

import numpy as np
from numpy.testing import assert_equal

from specparam.data import FitResults
from specparam.modes.items import OBJ_DESC
from specparam.modutils.dependencies import safe_import
from specparam.sim import sim_group_power_spectra

pd = safe_import('pandas')

from specparam.tests.tsettings import TEST_DATA_PATH, TEST_REPORTS_PATH
from specparam.tests.tdata import default_group_params
from specparam.tests.tutils import plot_test

from specparam.models.group import *

###################################################################################################
###################################################################################################

def test_group():
    """Check group object initializes properly."""

    # Note: doesn't assert the object itself, which returns false when `group_results` is empty
    #  This is due to the `__len__` used in the group object
    fg = SpectralGroupModel(verbose=False)
    assert isinstance(fg, SpectralGroupModel)

def test_getitem(tfg):
    """Check indexing, from custom `__getitem__` in group object."""

    assert tfg.results[0]

def test_iter(tfg):
    """Check iterating through group object."""

    for res in tfg.results:
        assert res

def test_has_data(tfg):
    """Test the has_data property attribute, with and without data."""

    assert tfg.results.has_model

    ntfg = SpectralGroupModel()
    assert not ntfg.data.has_data

def test_has_model(tfg):
    """Test the has_model property attribute, with and without model fits."""

    assert tfg.results.has_model

    ntfg = SpectralGroupModel()
    assert not ntfg.results.has_model

def test_n_peaks(tfg):
    """Test the n_peaks property attribute."""

    assert tfg.results.n_peaks_

def test_n_null(tfg):
    """Test the n_null_ property attribute."""

    # Since there should have been no failed fits, this should return 0
    assert tfg.results.n_null_ == 0

def test_null_inds(tfg):
    """Test the null_inds_ property attribute."""

    # Since there should be no failed fits, this should return an empty list
    assert tfg.results.null_inds_ == []

def test_fit_nk():
    """Test group fit, no knee."""

    n_spectra = 2
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params(), nlvs=0)

    tfg = SpectralGroupModel(verbose=False)
    tfg.fit(xs, ys)
    out = tfg.results.get_results()

    assert out
    assert len(out) == n_spectra
    assert isinstance(out[0], FitResults)
    assert np.all(out[1].aperiodic_params)

def test_fit_nk_noise():
    """Test group fit, no knee, on noisy data, to make sure nothing breaks."""

    n_spectra = 5
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params(), nlvs=1.0)

    tfg = SpectralGroupModel(max_n_peaks=8, verbose=False)
    tfg.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfg.results.has_model

def test_fit_knee():
    """Test group fit, with a knee."""

    n_spectra = 2
    ap_params = [50, 2, 1]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = sim_group_power_spectra(n_spectra, [1, 150], ap_params, gaussian_params, nlvs=0)

    tfg = SpectralGroupModel(aperiodic_mode='knee', verbose=False)
    tfg.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfg.results.has_model

def test_fit_progress(tfg):
    """Test running group fitting, with a progress bar."""

    tfg.fit(progress='tqdm')

def test_fg_fail():
    """Test group fit, in a way that some fits will fail.
    Also checks that model failures don't cause errors.
    """

    # Create some noisy spectra that will be hard to fit
    fs, ps = sim_group_power_spectra(10, [3, 6], [1, 1], [10, 1, 1], nlvs=10)

    # Use a fg with the max iterations set so low that it will fail to converge
    ntfg = SpectralGroupModel()
    ntfg.algorithm._maxfev = 5

    # Fit models, where some will fail, to see if it completes cleanly
    ntfg.fit(fs, ps)

    # Check that results are all
    for res in ntfg.results.get_results():
        assert res

    # Test that get_params works with failed model fits
    outs1 = ntfg.results.get_params('aperiodic_params')
    outs2 = ntfg.results.get_params('aperiodic_params', 'exponent')
    outs3 = ntfg.results.get_params('peak_params')
    outs4 = ntfg.results.get_params('peak_params', 0)
    outs5 = ntfg.results.get_params('gaussian_params', 2)

    # Test shortcut labels
    outs6 = ntfg.results.get_params('aperiodic')
    outs6 = ntfg.results.get_params('peak', 'CF')

    # Test the property attributes related to null model fits
    #   This checks that they do the right thing when there are null fits (failed fits)
    assert ntfg.results.n_null_ > 0
    assert ntfg.results.null_inds_

def test_drop():
    """Test function to drop results from group object."""

    n_spectra = 3
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params())

    tfg = SpectralGroupModel(verbose=False)

    # Test dropping one ind
    tfg.fit(xs, ys)

    drop_ind = 0
    tfg.results.drop(drop_ind)
    dropped_fres = tfg.results.group_results[drop_ind]
    for field in dropped_fres._fields:
        assert np.all(np.isnan(getattr(dropped_fres, field)))

    # Test dropping multiple inds
    tfg.fit(xs, ys)
    drop_inds = [0, 2]
    tfg.results.drop(drop_inds)

    for d_ind in drop_inds:
        dropped_fres = tfg.results.group_results[d_ind]
        for field in dropped_fres._fields:
            assert np.all(np.isnan(getattr(dropped_fres, field)))

    # Test that a group object that has had inds dropped still works with `get_params`
    cfs = tfg.results.get_params('peak_params', 1)
    exps = tfg.results.get_params('aperiodic_params', 'exponent')
    assert np.all(np.isnan(exps[drop_inds]))
    assert np.all(np.invert(np.isnan(np.delete(exps, drop_inds))))

def test_fit_par():
    """Test group fit, running in parallel."""

    n_spectra = 2
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params())

    tfg = SpectralGroupModel(verbose=False)
    tfg.fit(xs, ys, n_jobs=2)
    out = tfg.results.get_results()

    assert out
    assert len(out) == n_spectra
    assert isinstance(out[0], FitResults)
    assert np.all(out[1].aperiodic_params)

def test_print(tfg):
    """Check print method (alias)."""

    tfg.print_results()
    assert True

def test_save_model_report(tfg):

    file_name = 'test_group_model_report'
    tfg.save_model_report(0, file_name, TEST_REPORTS_PATH)

    assert os.path.exists(TEST_REPORTS_PATH / (file_name + '.pdf'))

def test_get_results(tfg):
    """Check get results method."""

    assert tfg.results.get_results()

def test_get_params(tfg):
    """Check get_params method."""

    for dname in ['aperiodic', 'peak', 'error', 'r_squared']:
        assert np.any(tfg.results.get_params(dname))

@plot_test
def test_plot(tfg, skip_if_no_mpl):
    """Check alias method for plot."""

    tfg.plot()

def test_load(tfg):
    """Test load into group object.
    Note: loads files from test_save_group in specparam/tests/io/test_models.py."""

    file_name_res = 'test_group_res'
    file_name_set = 'test_group_set'
    file_name_dat = 'test_group_dat'

    # Test loading just results
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load(file_name_res, TEST_DATA_PATH)
    assert len(ntfg.results.group_results) > 0
    # Test that settings and data are None
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(ntfg.algorithm, setting) is None
    assert ntfg.data.power_spectra is None

    # Test loading just settings
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load(file_name_set, TEST_DATA_PATH)
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(ntfg.algorithm, setting) is not None
    # Test that results and data are None
    for result in tfg.results._fields:
        assert np.all(np.isnan(getattr(ntfg.results, result)))
    assert ntfg.data.power_spectra is None

    # Test loading just data
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load(file_name_dat, TEST_DATA_PATH)
    assert ntfg.data.has_data
    # Test that settings and results are None
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(ntfg.algorithm, setting) is None
    for result in tfg.results._fields:
        assert np.all(np.isnan(getattr(ntfg.results, result)))

    # Test loading all elements
    ntfg = SpectralGroupModel(verbose=False)
    file_name_all = 'test_group_all'
    ntfg.load(file_name_all, TEST_DATA_PATH)
    assert len(ntfg.results.group_results) > 0
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(ntfg.algorithm, setting) is not None
    assert ntfg.data.has_data
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(ntfg.data, meta_dat) is not None

def test_report(skip_if_no_mpl):
    """Check that running the top level model method runs."""

    n_spectra = 2
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params())

    tfg = SpectralGroupModel(verbose=False)
    tfg.report(xs, ys)

    assert tfg

def test_get_model(tfg):
    """Check return of an individual model fit from a group object."""

    # Test with no ind (no data / results)
    tfm = tfg.get_model()
    assert tfm
    # Check that settings are copied over properly, but data and results are empty
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(tfg.algorithm, setting) == getattr(tfm.algorithm, setting)
    for result in tfg.results._fields:
        assert np.all(np.isnan(getattr(tfm.results, result)))
    assert not tfm.data.power_spectrum

    # Check without regenerating
    tfm0 = tfg.get_model(0, False)
    assert tfm0
    # Check that settings are copied over properly
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(tfg.algorithm, setting) == getattr(tfm0.algorithm, setting)

    # Check with regenerating
    tfm1 = tfg.get_model(1, True)
    assert tfm1
    # Check that regenerated model is created
    for result in tfg.results._fields:
        assert np.all(getattr(tfm1.results, result))

    # Test when object has no data (clear a copy of tfg)
    new_tfg = tfg.copy()
    new_tfg._reset_data_results(False, True, True, True)
    tfm2 = new_tfg.get_model(0, True)
    assert tfm2
    # Check that data info is copied over properly
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm2.data, meta_dat)

def test_get_group(tfg):
    """Check the return of a sub-sampled group object."""

    # Test with no inds
    nfg0 = tfg.get_group(None)
    assert isinstance(nfg0, SpectralGroupModel)
    assert nfg0.algorithm.get_settings() == tfg.algorithm.get_settings()
    assert nfg0.data.get_meta_data() == tfg.data.get_meta_data()

    # Check with list index
    inds1 = [1, 2]
    nfg1 = tfg.get_group(inds1)
    assert isinstance(nfg1, SpectralGroupModel)

    # Check with range index
    inds2 = range(0, 2)
    nfg2 = tfg.get_group(inds2)
    assert isinstance(nfg2, SpectralGroupModel)

    # Check that settings are copied over properly
    for setting in tfg.algorithm.definition.settings.names:
        assert getattr(tfg.algorithm, setting) == getattr(nfg1.algorithm, setting)
        assert getattr(tfg.algorithm, setting) == getattr(nfg2.algorithm, setting)

    # Check that data info is copied over properly
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(nfg1.data, meta_dat)
        assert getattr(nfg2.data, meta_dat)

    # Check that the correct data is extracted
    assert_equal(tfg.data.power_spectra[inds1, :], nfg1.data.power_spectra)
    assert_equal(tfg.data.power_spectra[inds2, :], nfg2.data.power_spectra)

    # Check that the correct results are extracted
    assert [tfg.results.group_results[ind] for ind in inds1] == nfg1.results.group_results
    assert [tfg.results.group_results[ind] for ind in inds2] == nfg2.results.group_results

def test_fg_to_df(tfg, tbands, skip_if_no_pandas):

    df1 = tfg.to_df(2)
    assert isinstance(df1, pd.DataFrame)
    df2 = tfg.to_df(tbands)
    assert isinstance(df2, pd.DataFrame)
