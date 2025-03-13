"""Tests for specparam.utils.select"""

from pytest import raises

from specparam.utils.select import *

###################################################################################################
###################################################################################################

def test_groupby():

    dat = [0, 1, 2, 3, 4, 5]
    assert groupby(dat, 3) == [[0, 1, 2], [3, 4, 5]]

    with raises(ValueError):
        groupby([0, 1, 2, 3], 3)

def test_nearest_ind():

    data = np.array([1, 2, 3, 4, 5])

    assert nearest_ind(data, 2.2) == 1
    assert nearest_ind(data, 3.7) == 3

def test_dict_select_keys():

    t_dict = {'a' : 1, 'b' : [1, 2, 3], 'c' : [4, 5, 6], 'd' : np.array([7, 8, 9])}
    keep = ['a', 'd']

    out = dict_select_keys(t_dict, keep)

    # Check the right number of items are kept, and that they are the ones specified
    assert len(out) == len(keep)
    for ke, va in out.items():
        assert ke in keep
