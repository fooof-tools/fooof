"""Tests for the specparam.models.group, including the group model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import os

import numpy as np
from numpy.testing import assert_equal

from specparam.metrics.definitions import METRICS
from specparam.models.utils import compare_model_objs
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

def test_n_properties(tfg):
    """Test the n_peaks & n_params property attributes."""

    assert np.all(tfg.results.n_peaks)
    assert np.all(tfg.results.n_params)

def test_n_null(tfg):
    """Test the n_null property attribute."""

    # Since there should have been no failed fits, this should return 0
    assert tfg.results.n_null == 0

def test_null_inds(tfg):
    """Test the null_inds property attribute."""

    # Since there should be no failed fits, this should return an empty list
    assert tfg.results.null_inds == []

def test_fit_nk():
    """Test group fit, no knee."""

    n_spectra = 2
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params(), nlvs=0)

    tfg = SpectralGroupModel(verbose=False)
    tfg.fit(xs, ys)
    out = tfg.results.get_results()

    assert out
    assert len(out) == n_spectra
    assert np.all(out[1].aperiodic_fit)

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

    xs, ys = sim_group_power_spectra(n_spectra, [1, 150], {'knee' : ap_params},
                                     {'gaussian' : gaussian_params}, nlvs=0)

    tfg = SpectralGroupModel(aperiodic_mode='knee', verbose=False)
    tfg.fit(xs, ys)

    # No accuracy checking here - just checking that it ran
    assert tfg.results.has_model

def test_fit_custom_metrics():

    metrics = list(METRICS.keys())

    n_spectra = 2
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params(), nlvs=0)

    tfg = SpectralGroupModel(metrics=metrics, verbose=False)
    tfg.fit(xs, ys)

    for fres in tfg.results.group_results:
        for metric in metrics:
            assert isinstance(fres.metrics[metric], float)

def test_fit_progress(tfg):
    """Test running group fitting, with a progress bar."""

    tfg.fit(progress='tqdm')
    assert tfg.results.has_model

def test_fg_fail():
    """Test group fit, in a way that some fits will fail.
    Also checks that model failures don't cause errors.
    """

    # Create some noisy spectra that will be hard to fit
    n_spectra = 10
    fs, ps = sim_group_power_spectra(\
        n_spectra, [3, 6], {'fixed' : [1, 1]}, {'gaussian' : [10, 1, 1]}, nlvs=10)

    # Use a fg with the max iterations set so low that it will fail to converge
    ntfg = SpectralGroupModel()
    ntfg.algorithm._cf_settings.maxfev = 5

    # Fit models, where some will fail, to see if it completes cleanly
    ntfg.fit(fs, ps)

    # Check that results are all properly organized
    assert len(ntfg.results) == n_spectra
    for res in ntfg.results.get_results():
        assert res

    # Test the property attributes related to null model fits
    #   This checks that they do the right thing when there are null fits (failed fits)
    assert ntfg.results.n_null > 0
    assert ntfg.results.null_inds

    # Test that get_params works with failed model fits
    outs1 = ntfg.results.get_params('aperiodic')
    outs2 = ntfg.results.get_params('aperiodic', 'exponent')
    outs3 = ntfg.results.get_params('peak')
    outs4 = ntfg.results.get_params('peak', 0)
    outs5 = ntfg.results.get_params('peak', 'CF')
    # TODO
    #outs6 = ntfg.results.get_params('peak', 2, version='fit')

    # Check that null ind values are nan
    for null_ind in ntfg.results.null_inds:
        assert np.isnan(ntfg.results.get_params('aperiodic', 'exponent')[null_ind])
        assert np.isnan(ntfg.results.get_metrics('error', 'mae')[null_ind])

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
    for field in [el for el in dropped_fres._fields if 'params' in el]:
        assert np.all(np.isnan(getattr(dropped_fres, field)))
    assert np.all(np.isnan(list(dropped_fres.metrics.values())))

    # Test dropping multiple inds
    tfg.fit(xs, ys)
    drop_inds = [0, 2]
    tfg.results.drop(drop_inds)

    for d_ind in drop_inds:
        dropped_fres = tfg.results.group_results[d_ind]
        for field in [el for el in dropped_fres._fields if 'params' in el]:
            assert np.all(np.isnan(getattr(dropped_fres, field)))
    assert np.all(np.isnan(list(dropped_fres.metrics.values())))

    # Test that a group object that has had inds dropped still works with `get_params`
    cfs = tfg.get_params('peak', 1)
    exps = tfg.get_params('aperiodic', 'exponent')
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
    assert np.all(out[1].aperiodic_fit)

def test_print(tfg):
    """Check print method (alias)."""

    tfg.print_results()
    assert True

def test_save_model_report(tfg, skip_if_no_mpl):

    file_name = 'test_group_model_report'
    tfg.save_model_report(0, file_name, TEST_REPORTS_PATH)

    assert os.path.exists(TEST_REPORTS_PATH / (file_name + '.pdf'))

def test_get_results(tfg):
    """Check get results method."""

    assert tfg.results.get_results()

def test_get_params(tfg):
    """Check get_params method."""

    for component in tfg.modes.components:
        assert np.any(tfg.get_params(component))
        for pname in getattr(tfg.modes, component).params.labels:
            assert np.any(tfg.get_params(component, pname))

@plot_test
def test_plot(tfg, skip_if_no_mpl):
    """Check alias method for plot."""

    tfg.plot()

def test_load(tfg):
    """Test load into group object.
    Note: loads files from test_save_group in specparam/tests/io/test_models.py."""

    # Test loading just results
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load('test_group_res', TEST_DATA_PATH)
    assert len(ntfg.results.group_results) > 0
    # Test that settings and data are None
    for setting in tfg.algorithm.settings.names:
        assert getattr(ntfg.algorithm.settings, setting) is None
    assert ntfg.data.power_spectra is None

    # Test loading just settings
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load('test_group_set', TEST_DATA_PATH)
    assert tfg.algorithm.settings.values == ntfg.algorithm.settings.values
    # Test that results and data are None
    for component in tfg.modes.components:
        assert not getattr(ntfg.results.params, component).has_params
    assert ntfg.data.power_spectra is None

    # Test loading just data
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load('test_group_dat', TEST_DATA_PATH)
    assert ntfg.data.has_data
    # Test that settings and results are None
    for setting in tfg.algorithm.settings.names:
        assert getattr(ntfg.algorithm.settings, setting) is None
    for component in tfg.modes.components:
        assert not getattr(ntfg.results.params, component).has_params

    # Test loading all elements
    ntfg = SpectralGroupModel(verbose=False)
    ntfg.load('test_group_all', TEST_DATA_PATH)
    assert compare_model_objs([tfg, ntfg], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])
    assert len(ntfg.results.group_results) > 0

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
    tfm_null = tfg.get_model()
    assert tfm_null
    # Check that settings are copied over properly, but data and results are empty
    assert tfg.algorithm.settings.values == tfm_null.algorithm.settings.values
    assert not tfm_null.data.has_data
    assert not tfm_null.results.has_model

    # Check without regenerating
    tfm0 = tfg.get_model(0, False)
    assert tfm0
    # Check that settings are copied over properly
    assert tfg.algorithm.settings.values == tfm0.algorithm.settings.values

    # Check with regenerating
    tfm1 = tfg.get_model(1, True)
    assert tfm1
    # Check that parameters are copied and that regenerated model is created
    for component in tfg.modes.components:
        assert getattr(tfm1.results.params, component).has_params
    assert np.all(tfm1.results.model.modeled_spectrum)

    # Test when object has no data (clear a copy of tfg)
    new_tfg = tfg.copy()
    new_tfg._reset_data_results(False, True, True, True)
    tfm2 = new_tfg.get_model(0, True)
    assert tfm2
    # Check that data info is copied over properly
    for meta_dat in tfg.data._meta_fields:
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
    assert tfg.algorithm.settings.values == nfg1.algorithm.settings.values
    assert tfg.algorithm.settings.values == nfg2.algorithm.settings.values

    # Check that data info is copied over properly
    for meta_dat in tfg.data._meta_fields:
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
