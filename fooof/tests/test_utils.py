"""Test functions for FOOOF utils."""

from py.test import raises
import numpy as np

from fooof.utils import *
from fooof.core.utils import *
from fooof.core.modutils import *

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

    for ke, va in out.items():
        if ke in keep:
            continue
        assert False

def test_trim_psd():

    f_in = np.array([0., 1., 2., 3., 4., 5.])
    p_in = np.array([1., 2., 3., 4., 5., 6.])

    f_out, p_out = trim_psd(f_in, p_in, [2., 4.])

    assert np.array_equal(f_out, np.array([2., 3., 4.]))
    assert np.array_equal(p_out, np.array([3., 4., 5.]))

def test_get_obj_desc():

    assert get_obj_desc()
