"""Test functions for FOOOF utils."""

from py.test import raises

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

    fm_settings = get_settings(tfm)
    assert fm_settings

    fg_settings = get_settings(tfg)
    assert fg_settings

def test_compare_settings(tfm, tfg):

    # Check with FOOOF object
    tfm2 = tfm.copy()

    assert compare_settings([tfm, tfm2])

    tfm2.peak_width_limits = [2, 4]
    tfm2._reset_internal_settings()

    assert not compare_settings([tfm, tfm2])

    # Check with FOOOFGroup object
    tfg2 = tfg.copy()

    assert compare_settings([tfg, tfg2])

    tfg2.peak_width_limits = [2, 4]
    tfg2._reset_internal_settings()

    assert not compare_settings([tfg, tfg2])

def test_combine_fooofs(tfm):

    tfm2 = tfm.copy()
    tfm3 = tfm.copy()

    # Check combining 2 FOOOFs
    fg1 = combine_fooofs([tfm, tfm2])
    assert fg1
    assert len(fg1) == 2
    assert compare_settings([fg1, tfm])
    assert fg1.group_results[0] == tfm.get_results()
    assert fg1.group_results[-1] == tfm2.get_results()

    # Check combining 3 FOOOFs
    fg2 = combine_fooofs([tfm, tfm2, tfm3])
    assert fg2
    assert len(fg2) == 3
    assert compare_settings([fg2, tfm])
    assert fg2.group_results[0] == tfm.get_results()
    assert fg2.group_results[-1] == tfm3.get_results()

def test_combine_fooof_groups(tfg):

    tfg2 = tfg.copy()
    tfg3 = tfg.copy()

    # Check combining 2 FOOOFGroups
    nfg1 = combine_fooof_groups([tfg, tfg2])
    assert nfg1
    assert len(nfg1) == len(tfg) + len(tfg2)
    assert compare_settings([nfg1, tfg, tfg2])
    assert nfg1.group_results[0] == tfg.group_results[0]
    assert nfg1.group_results[-1] == tfg2.group_results[-1]

    # Check combining 3 FOOOFGroups
    nfg2 = combine_fooof_groups([tfg, tfg2, tfg3])
    assert nfg2
    assert len(nfg2) == len(tfg) + len(tfg2) + len(tfg3)
    assert compare_settings([nfg2, tfg, tfg2, tfg3])
    assert nfg2.group_results[0] == tfg.group_results[0]
    assert nfg2.group_results[-1] == tfg3.group_results[-1]

def test_combine_errors(tfm, tfg):

    # Check incompatible settings error with FOOOFs
    tfm2 = tfm.copy()
    tfm2.peak_width_limits = [2, 4]
    tfm2._reset_internal_settings()

    with raises(ValueError):
        combine_fooofs([tfm, tfm2])

    # Check incompatible settings error with FOOOFGroups
    tfg2 = tfg.copy()
    tfg2.peak_width_limits = [2, 4]
    tfg2._reset_internal_settings()

    assert tfg.peak_width_limits == [0.5, 12]
    assert tfg2.peak_width_limits == [2, 4]

    with raises(ValueError):
        combine_fooof_groups([tfg, tfg2])
