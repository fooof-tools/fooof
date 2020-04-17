"""Test functions for fooof.analysis.periodic."""

import numpy as np

from fooof.analysis.periodic import *

###################################################################################################
###################################################################################################

def test_get_band_peak_fm(tfm):

    assert np.all(get_band_peak_fm(tfm, (8, 12)))

def test_get_band_peak_fg(tfg):

    assert np.all(get_band_peak_fg(tfg, (8, 12)))

def test_get_band_peak_group():

    data = np.array([[10, 1, 1.8, 0], [13, 1, 2, 2], [14, 2, 4, 2]])

    out1 = get_band_peak_group(data, [8, 12], 3)
    assert out1.shape == (3, 3)
    assert np.array_equal(out1[0, :], [10, 1, 1.8])

    out2 = get_band_peak_group(data, [12, 16], 3)
    assert out2.shape == (3, 3)
    assert np.array_equal(out2[2, :], [14, 2, 4])

def test_get_band_peak():

    data = np.array([[10, 1, 1.8], [14, 2, 4]])

    # Test single result
    assert np.array_equal(get_band_peak(data, [10, 12]), [10, 1, 1.8])

    # Test no results - returns nan
    assert np.all(np.isnan(get_band_peak(data, [4, 8])))

    # Test multiple results - return all
    assert np.array_equal(get_band_peak(data, [10, 15], select_highest=False),
                          np.array([[10, 1, 1.8], [14, 2, 4]]))

    # Test multiple results - return one
    assert np.array_equal(get_band_peak(data, [10, 15], select_highest=True),
                          np.array([14, 2, 4]))

    # Test applying a threshold
    assert np.array_equal(get_band_peak(data, [10, 15], threshold=1.5, select_highest=False),
                          np.array([14, 2, 4]))

def test_get_highest_peak():

    data = np.array([[10, 1, 1.8], [14, 2, 4], [12, 3, 2]])

    assert np.array_equal(get_highest_peak(data), [12, 3, 2])

def test_threshold_peaks():

    # Check it works, with a standard power threshold
    data = np.array([[10, 1, 1.8], [14, 2, 4], [12, 3, 2.5]])
    assert np.array_equal(threshold_peaks(data, 2.5), np.array([[12, 3, 2.5]]))

    # Check it works using a bandwidth threshold
    data = np.array([[10, 1, 1.8], [14, 2, 4], [12, 3, 2.5]])
    assert np.array_equal(threshold_peaks(data, 2, param='BW'),
                          np.array([[14, 2, 4], [12, 3, 2.5]]))

    # Check it works with an [n_peaks, 4] array, as from FOOOFGroup
    data = np.array([[10, 1, 1.8, 0], [13, 1, 2, 2], [14, 2, 4, 2]])
    assert np.array_equal(threshold_peaks(data, 1.5), np.array([[14, 2, 4, 2]]))

def test_empty_inputs():

    data = np.empty(shape=[0, 3])

    assert np.all(get_band_peak(data, [8, 12]))
    assert np.all(get_highest_peak(data))
    assert np.all(threshold_peaks(data, 1))

    data = np.empty(shape=[0, 4])

    assert np.all(get_band_peak_group(data, [8, 12], 0))
