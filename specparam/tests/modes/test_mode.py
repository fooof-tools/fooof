"""Tests for specparam.modes.mode."""

from collections import OrderedDict

from specparam.modes.params import ParamDefinition

from specparam.modes.mode import *

###################################################################################################
###################################################################################################

def test_mode():

    def tfit(xs, *params):
        return xs

    params = ParamDefinition(OrderedDict({
        'a' : 'a desc',
        'b' : 'b desc',
    }))

    tmode = Mode(name='tmode', component='periodic', description='test_desc',
                 func=tfit, jacobian=None, params=params,
                 freq_space='linear', powers_space='linear')
    assert tmode
    assert tmode.n_params == params.n_params
