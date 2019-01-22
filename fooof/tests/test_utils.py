"""Test functions for FOOOF utils."""

import numpy as np

from fooof.utils import *

###################################################################################################
###################################################################################################

def test_trim_spectrum():

    f_in = np.array([0., 1., 2., 3., 4., 5.])
    p_in = np.array([1., 2., 3., 4., 5., 6.])

    f_out, p_out = trim_spectrum(f_in, p_in, [2., 4.])

    assert np.array_equal(f_out, np.array([2., 3., 4.]))
    assert np.array_equal(p_out, np.array([3., 4., 5.]))

def test_get_settings(tfm, tfg):

    for f_obj in [tfm, tfg]:
        assert get_settings(f_obj)

def test_get_data_info(tfm, tfg):

    for f_obj in [tfm, tfg]:
        assert get_data_info(f_obj)

def test_compare_settings(tfm, tfg):

    for f_obj in [tfm, tfg]:
        f_obj2 = f_obj.copy()

        assert compare_settings([f_obj, f_obj2])

        f_obj2.peak_width_limits = [2, 4]
        f_obj2._reset_internal_settings()

        assert not compare_settings([f_obj, f_obj2])

def test_compare_data_info(tfm, tfg):

    for f_obj in [tfm, tfg]:
        f_obj2 = f_obj.copy()

        assert compare_data_info([f_obj, f_obj2])

        f_obj2.freq_range = [5, 25]

        assert not compare_data_info([f_obj, f_obj2])
