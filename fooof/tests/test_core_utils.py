"""Tests for fooof.core.utils."""

from collections.abc import Iterable
from itertools import repeat

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

def test_check_iter():

    # Note: generator case not tested

    # Check that a number input becomes an iterable
    out = check_iter(12, 3)
    assert isinstance(out, Iterable)
    assert isinstance(out, repeat)

    # Check that single list becomes repeat iterable
    out = check_iter([1, 1], 2)
    assert isinstance(out, Iterable)
    assert isinstance(out, repeat)

    # Check that a list of lists, of right length stays list of list
    out = check_iter([[1, 1], [1, 1], [1, 1]], 3)
    assert isinstance(out, Iterable)
    assert isinstance(out, list)
    assert isinstance(out[0], list)

def test_check_flat():

    # Check an empty list stays the same
    assert check_flat([]) == []

    # Check an already flat list gets left the same
    lst = [1, 2, 3, 4]
    flat_lst = check_flat(lst)
    assert flat_lst == lst

    # Check a nested list gets flattened
    lst = [[1, 2], [3, 4]]
    flat_lst = check_flat(lst)
    for el in flat_lst:
        assert isinstance(el, int)
    assert len(flat_lst) == 4
