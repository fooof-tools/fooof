"""Tests for the specparam.objs.time, including the time model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np

from specparam.sim import sim_spectrogram

from specparam.tests.settings import TEST_DATA_PATH
from specparam.tests.tutils import default_group_params, plot_test

from specparam.objs.time import *

###################################################################################################
###################################################################################################

def test_time_model():
    """Check time object initializes properly."""

    # Note: doesn't assert the object itself, which returns false empty
    ft = SpectralTimeModel(verbose=False)
    assert isinstance(ft, SpectralTimeModel)

def test_time_iter(tft):

    for out in tft:
        print(out)
        assert out

def test_time_getitem(tft):

    assert tft[0]

def test_time_fit():

    n_windows = 10
    xs, ys = sim_spectrogram(n_windows, *default_group_params())

    tft = SpectralTimeModel(verbose=False)
    tft.fit(xs, ys)

    results = tft.get_results()

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

def test_time_load(tbands):

    file_name_res = 'test_time_res'
    file_name_set = 'test_time_set'
    file_name_dat = 'test_time_dat'

    # Test loading results
    tft = SpectralTimeModel(verbose=False)
    tft.load(file_name_res, TEST_DATA_PATH, peak_org=tbands)
    assert tft.time_results
