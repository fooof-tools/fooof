"""Tests for specparam.modes.params."""

from collections import OrderedDict

from specparam.modes.params import *

###################################################################################################
###################################################################################################

def test_param_definition():

    params_dict = OrderedDict({
        'a' : 'a desc',
        'b' : 'b desc',
    })

    params_obj = ParamDefinition(params_dict)

    assert isinstance(params_obj, ParamDefinition)
    assert params_obj.n_params == len(params_dict)
    assert params_obj.labels == list(params_dict.keys())
    assert params_obj.indices == {'a' : 0, 'b' : 1}
    assert params_obj.descriptions == params_dict
