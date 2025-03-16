"""Tests for specparam.modes.mode."""

from specparam.modes.mode import *

###################################################################################################
###################################################################################################

def test_mode():

    def tfit(xs, *params):
        return xs
    params = ['a', 'b']
    param_description = {'a' : 1, 'b' : 2}

    tmode = Mode(name='tmode', component='periodic', description='test_desc',
                 func=tfit, params=params, param_description=param_description,
                 freq_space='linear', powers_space='linear')
    assert tmode
    assert tmode.n_params == len(params)
    assert isinstance(tmode.param_indices, dict)
