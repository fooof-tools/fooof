"""Test functions for fooof.utils."""

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

def test_get_info(tfm, tfg):

    for f_obj in [tfm, tfg]:
        assert get_info(f_obj, 'settings')
        assert get_info(f_obj, 'meta_data')
        assert get_info(f_obj, 'results')

def test_compare_info(tfm, tfg):

    for f_obj in [tfm, tfg]:

        f_obj2 = f_obj.copy()

        assert compare_info([f_obj, f_obj2], 'settings')
        f_obj2.peak_width_limits = [2, 4]
        f_obj2._reset_internal_settings()
        assert not compare_info([f_obj, f_obj2], 'settings')

        assert compare_info([f_obj, f_obj2], 'meta_data')
        f_obj2.freq_range = [5, 25]
        assert not compare_info([f_obj, f_obj2], 'meta_data')
