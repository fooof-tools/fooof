"""Tests for specparam.utils.array."""

import numpy as np

from specparam.utils.array import *

###################################################################################################
###################################################################################################

def test_normalize():

    arr1 = np.array([0, 0.25, 0.5])
    norm_arr1 = normalize(arr1)
    assert np.array_equal(norm_arr1, np.array([0.0, 0.5, 1.0]))

    arr2 = np.array([0, 5, 10])
    norm_arr2 = normalize(arr2)
    assert np.array_equal(norm_arr2, np.array([0.0, 0.5, 1.0]))

def test_unlog():

    orig = np.array([1, 2, 3, 4])
    logged = np.log10(orig)
    unlogged = unlog(logged)
    assert np.array_equal(orig, unlogged)

def test_compute_arr_desc():

    data1_full = np.array([1., 2., 3., 4., 5.])
    minv, maxv, meanv = compute_arr_desc(data1_full)
    for val in [minv, maxv, meanv]:
        assert isinstance(val, float)

    data1_nan = np.array([np.nan, 2., 3., np.nan, 5.])
    minv, maxv, meanv = compute_arr_desc(data1_nan)
    for val in [minv, maxv, meanv]:
        assert isinstance(val, float)
