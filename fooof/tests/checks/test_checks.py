"""Test functions for fooof.checks."""

from fooof.checks import *

###################################################################################################
###################################################################################################

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

def test_compute_pointwise_error_fm(tfm):

    compute_pointwise_error_fm(tfm, True, True)

def test_compute_pointwise_error_fg(tfg):

    compute_pointwise_error_fg(tfg, True, True)
