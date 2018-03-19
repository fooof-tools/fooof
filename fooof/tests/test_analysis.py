"""Test functions for FOOOF analysis."""

import numpy as np

from fooof.analysis import *

###################################################################################################
###################################################################################################

def test_get_band_peak_group():

    dat = np.array([[10, 1, 1.8, 0], [13, 1, 2, 2], [14, 2, 4, 2]])

    out1 = get_band_peak_group(dat, [8, 12], 3)
    assert out1.shape == (3, 3)
    assert np.array_equal(out1[0, :], [10, 1, 1.8])

    out2 = get_band_peak_group(dat, [12, 16], 3)
    assert out2.shape == (3, 3)
    assert np.array_equal(out2[2, :], [14, 2, 4])

def test_get_band_peak():

    dat = np.array([[10, 1, 1.8], [14, 2, 4]])

    # Test single result
    assert np.array_equal(get_band_peak(dat, [10, 12]), [10, 1, 1.8])

    # Test no results - returns nan
    assert np.all(np.isnan(get_band_peak(dat, [4, 8])))

    # Test muliple results - return all
    assert np.array_equal(get_band_peak(dat, [10, 15], ret_one=False), [[10, 1, 1.8], [14, 2, 4]])

    # Test multiple results - return one
    assert np.array_equal(get_band_peak(dat, [10, 15], ret_one=True), [14, 2, 4])

def test_get_highest_amp_osc():

    dat = np.array([[10, 1, 1.8], [14, 2, 4], [12, 3, 2]])

    assert np.array_equal(get_highest_amp_peak(dat), [12, 3, 2])

def test_empty_inputs():

    dat = np.empty(shape=[0, 3])

    assert np.all(get_band_peak(dat, [8, 12]))
    assert np.all(get_highest_amp_peak(dat))

    dat = np.empty(shape=[0, 4])

    assert np.all(get_band_peak_group(dat, [8, 12], 0))
