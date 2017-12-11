"""Test functions for FOOOF analysis."""

import numpy as np

from fooof.analysis import *

###################################################################################################
###################################################################################################

def test_get_band_osc():

    dat = np.array([[10, 1, 1.8], [14, 2, 4]])
    assert np.array_equal(get_band_osc(dat, [10, 12]), [10, 1, 1.8])
    assert np.all(np.isnan(get_band_osc(dat, [4, 8])))
    assert np.array_equal(get_band_osc(dat, [10, 14], ret_one=False), [[10, 1, 1.8],[14, 2, 4]])

def test_get_highest_power_osc():

    dat = np.array([[10, 1, 1.8], [14, 2, 4], [12, 3, 2]])
    assert np.array_equal(get_highest_power_osc(dat), [12, 3, 2])

def test_empty_inputs():

    dat = np.empty(shape=[0, 3])
    assert np.all(get_band_osc(dat, [8, 12]))
    assert np.all(get_highest_power_osc(dat))
