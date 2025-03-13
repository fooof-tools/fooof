"""Tests for specparam.measures.properties."""

import numpy as np

from specparam.measures.properties import *

###################################################################################################
###################################################################################################

def test_compute_average():

    data = np.array([[0., 1., 2., 3., 4., 5.],
                     [1., 2., 3., 4., 5., 6.],
                     [5., 6., 7., 8., 9., 8.]])

    out1 = compute_average(data, 'mean')
    assert isinstance(out1, np.ndarray)

    out2 = compute_average(data, 'median')
    assert not np.array_equal(out2, out1)

    def _average_callable(data):
        return np.mean(data, axis=0)
    out3 = compute_average(data, _average_callable)
    assert isinstance(out3, np.ndarray)
    assert np.array_equal(out3, out1)

def test_compute_dispersion():

    data = np.array([[0., 1., 2., 3., 4., 5.],
                     [1., 2., 3., 4., 5., 6.],
                     [5., 6., 7., 8., 9., 8.]])

    out1 = compute_dispersion(data, 'var')
    assert isinstance(out1, np.ndarray)

    out2 = compute_dispersion(data, 'std')
    assert not np.array_equal(out2, out1)

    out3 = compute_dispersion(data, 'sem')
    assert not np.array_equal(out3, out1)

    def _dispersion_callable(data):
        return np.std(data, axis=0)
    out4 = compute_dispersion(data, _dispersion_callable)
    assert isinstance(out4, np.ndarray)
    assert np.array_equal(out4, out2)

def test_compute_presence():

    data1_full = np.array([0, 1, 2, 3, 4])
    data1_nan = np.array([0, np.nan, 2, 3, np.nan])
    assert compute_presence(data1_full) == 1.0
    assert compute_presence(data1_nan) == 0.6
    assert compute_presence(data1_nan, output='percent') == 60.0

    data2_full = np.array([[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]])
    data2_nan = np.array([[0, np.nan, 2, 3, np.nan], [np.nan, 6, 7, 8, np.nan]])
    assert np.array_equal(compute_presence(data2_full), np.array([1.0, 1.0, 1.0, 1.0, 1.0]))
    assert np.array_equal(compute_presence(data2_nan), np.array([0.5, 0.5, 1.0, 1.0, 0.0]))
    assert np.array_equal(compute_presence(data2_nan, output='percent'),
                          np.array([50.0, 50.0, 100.0, 100.0, 0.0]))
    assert compute_presence(data2_full, average=True) == 1.0
    assert compute_presence(data2_nan, average=True) == 0.6
