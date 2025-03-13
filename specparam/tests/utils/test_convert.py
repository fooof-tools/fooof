"""Tests for specparam.utils.convert."""

import numpy as np

from specparam.utils.convert import *

###################################################################################################
###################################################################################################

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
