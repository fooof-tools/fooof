"""Tests for FOOOF core.utils."""

from fooof import FOOOF
from fooof.core.utils import *

from py.test import raises

###################################################################################################
###################################################################################################

def test_group_three():

    dat = [0, 1, 2, 3, 4, 5]
    assert group_three(dat) == [[0, 1, 2], [3, 4, 5]]

    with raises(ValueError):
        group_three([0, 1, 2, 3])

def test_dict_array_to_lst():

    t_dict = {'a' : 1, 'b' : np.array([1, 2, 3]), 'c' : [4, 5, 6], 'd' : np.array([7, 8, 9])}

    out = dict_array_to_lst(t_dict)

    for ke, va in out.items():
        assert not isinstance(va, np.ndarray)

def test_dict_lst_to_array():

    t_dict = {'a' : 1, 'b' : [1, 2, 3], 'c' : [4, 5, 6], 'd' : np.array([7, 8, 9])}
    mk_array = ['b', 'c']

    out = dict_lst_to_array(t_dict, mk_array)

    for ke, va in out.items():
        if ke in mk_array:
            assert isinstance(va, np.ndarray)

def test_dict_select_keys():

    t_dict = {'a' : 1, 'b' : [1, 2, 3], 'c' : [4, 5, 6], 'd' : np.array([7, 8, 9])}
    keep = ['a', 'd']

    out = dict_select_keys(t_dict, keep)

    # Check the right number of items are kept, and that they are the ones specified
    assert len(out) == len(keep)
    for ke, va in out.items():
        assert ke in keep

def test_check_array_dim():

    out = check_array_dim(np.array([]))
    assert out.shape == (0, 3)

    out = check_array_dim(np.array([1, 2, 3]))
    assert out.shape == (0, 3)

def test_get_obj_desc():

    desc =  get_obj_desc()

    tfm = FOOOF()
    objs = dir(tfm)

    # Test that everything in dict is a valid component of the fooof object
    for ke, va in desc.items():
        for it in va:
            assert it in objs

def test_get_data_indices():

    indices_fixed = get_data_indices('fixed')
    assert indices_fixed
    for ke, va in indices_fixed.items():
        if ke == 'knee':
            assert not va
        else:
            assert isinstance(va, int)

    indices_knee = get_data_indices('knee')
    assert indices_knee
    for ke, va in indices_knee.items():
        assert isinstance(va, int)
