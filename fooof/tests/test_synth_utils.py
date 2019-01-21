"""Test functions for FOOOF synth.utils"""

from collections import Iterable
from itertools import repeat

from fooof.synth.utils import _check_flat, _check_iter

###################################################################################################
###################################################################################################

def test_check_iter():

    # Note: generator case not tested

    # Check that a number input becomes an iterable
    out = _check_iter(12, 3)
    assert isinstance(out, Iterable)
    assert isinstance(out, repeat)

    # Check that single list becomes repeat iterable
    out = _check_iter([1, 1], 2)
    assert isinstance(out, Iterable)
    assert isinstance(out, repeat)

    # Check that a list of lists, of right length stays list of list
    out = _check_iter([[1, 1], [1, 1], [1, 1]], 3)
    assert isinstance(out, Iterable)
    assert isinstance(out, list)
    assert isinstance(out[0], list)

def test_check_flat():

    # Check an empty list stays the same
    assert _check_flat([]) == []

    # Check an already flat list gets left the same
    lst = [1, 2, 3, 4]
    flat_lst = _check_flat(lst)
    assert flat_lst == lst

    # Check a nested list gets flattened
    lst = [[1, 2], [3, 4]]
    flat_lst = _check_flat(lst)
    for el in flat_lst:
        assert isinstance(el, int)
    assert len(flat_lst) == 4
