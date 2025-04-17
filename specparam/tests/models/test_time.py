"""Tests for the specparam.models.time, including the time model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np

from specparam.sim import sim_spectrogram
from specparam.models.utils import compare_model_objs
from specparam.modutils.dependencies import safe_import

pd = safe_import('pandas')

from specparam.tests.tsettings import TEST_DATA_PATH
from specparam.tests.tdata import default_group_params
from specparam.tests.tutils import plot_test

from specparam.models.time import *

###################################################################################################
###################################################################################################

def test_time_model():
    """Check time object initializes properly."""

    # Note: doesn't assert the object itself, which returns false empty
    ft = SpectralTimeModel(verbose=False)
    assert isinstance(ft, SpectralTimeModel)

def test_time_getitem(tft):

    assert tft.results[0]

def test_time_iter(tft):

    for out in tft.results:
        assert out

def test_time_n_properties(tft):

    assert np.all(tft.results.n_peaks)
    assert np.all(tft.results.n_params)

def test_time_fit():

    n_windows = 10
    xs, ys = sim_spectrogram(n_windows, *default_group_params())

    tft = SpectralTimeModel(verbose=False)
    tft.fit(xs, ys)

    results = tft.results.get_results()

    assert results
    assert isinstance(results, dict)
    for key in results.keys():
        assert np.all(results[key])
        assert len(results[key]) == n_windows

def test_time_print(tft):

    tft.print_results()

@plot_test
def test_time_plot(tft, skip_if_no_mpl):

    tft.plot()

def test_time_report(skip_if_no_mpl):

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())

    tft = SpectralTimeModel(verbose=False)
    tft.report(xs, ys)

    assert tft

def test_time_load(tft):

    # Test loading results
    ntft = SpectralTimeModel(verbose=False)
    ntft.load('test_time_res', TEST_DATA_PATH)
    assert ntft.results.time_results

    # Test loading settings
    ntft = SpectralTimeModel(verbose=False)
    ntft.load('test_time_set', TEST_DATA_PATH)
    assert ntft.algorithm.get_settings()

    # Test loading data
    ntft = SpectralTimeModel(verbose=False)
    ntft.load('test_time_dat', TEST_DATA_PATH)
    assert np.all(ntft.data.spectrogram)

    # Test loading all elements
    ntft = SpectralTimeModel(verbose=False)
    ntft.load('test_time_all', TEST_DATA_PATH)
    assert compare_model_objs([tft, ntft], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])

def test_time_drop():

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())
    tft = SpectralTimeModel(verbose=False)

    tft.fit(xs, ys)
    drop_inds = [0, 2]
    tft.results.drop(drop_inds)
    assert len(tft.results) == n_windows
    for dind in drop_inds:
        for key in tft.results.time_results:
            assert np.isnan(tft.results.time_results[key][dind])

def test_time_get_group(tft):

    nft0 = tft.get_group(None)
    assert isinstance(nft0, SpectralTimeModel)

    inds = [1, 2]

    nft = tft.get_group(inds)
    assert isinstance(nft, SpectralTimeModel)
    assert len(nft.results.group_results) == len(inds)
    assert len(nft.results.time_results[list(nft.results.time_results.keys())[0]]) == len(inds)
    assert nft.data.spectrogram.shape[-1] == len(inds)

    nfg = tft.get_group(inds, 'group')
    assert not isinstance(nfg, SpectralTimeModel)
    assert len(nfg.results.group_results) == len(inds)

def test_time_to_df(tft, tbands, skip_if_no_pandas):

    df0 = tft.to_df()
    assert isinstance(df0, pd.DataFrame)
    df1 = tft.to_df(2)
    assert isinstance(df1, pd.DataFrame)
    df2 = tft.to_df(tbands)
    assert isinstance(df2, pd.DataFrame)
