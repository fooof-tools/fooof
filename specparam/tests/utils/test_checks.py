"""Tests for specparam.utils.checks."""

from pytest import raises

from collections.abc import Iterable
from itertools import repeat

import numpy as np

from specparam.utils.checks import *

###################################################################################################
###################################################################################################

def test_check_input_options():

    value = 'a'
    options = ['a', 'b', 'c']

    out1 = check_input_options(value, options, 'tinput')
    assert out1 == value

    with raises(ValueError):
        out2 = check_input_options('d', options, 'tinput')

def test_check_selection():

    opts = {'a' : 1, 'b' : 2}

    out = check_selection('a', opts, int)
    assert out == 1

    out = check_selection(None, opts, int)
    assert out is None

    with raises(ValueError):
        out = check_selection('c', opts, int)

    # Check valid & invalid instance input
    out = check_selection(5, opts, int)
    assert out == 5
    with raises(ValueError):
        out = check_selection(5.5, opts, int)

    # Check valid & invalid class input
    out = check_selection(int, opts, int)
    assert out == int
    with raises(ValueError):
        out = check_selection(float, opts, int)

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

def test_check_inds():

    # Test single integer input
    assert check_inds(1) == np.array([1])

    # Test list of integer input
    assert np.array_equal(check_inds([0, 2]), np.array([0, 2]))

    # Test range input
    assert np.array_equal(check_inds(range(0, 2)), np.array([0, 1]))

    # Test int array input
    assert np.array_equal(check_inds(np.array([1, 2, 3])), np.array([1, 2, 3]))

    # Test boolean array input
    assert np.array_equal(check_inds(np.array([True, False, True])), np.array([0, 2]))

    # Check None inputs, including length input
    assert isinstance(check_inds(None), slice)
    assert isinstance(check_inds(None, 4), range)

def test_check_all_none():

    assert check_all_none([None])
    assert check_all_none([None, None])
    assert check_all_none((None,))

    assert not check_all_none([])
    assert not check_all_none([1, None])
    assert not check_all_none([1, 2, 3])
