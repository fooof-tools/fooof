"""Test functions for specparam.convert.params."""

from specparam.convert.params import *

###################################################################################################
###################################################################################################

def test_compute_peak_height(tfm):

    for spacing in ['log', 'linear']:
        for op in ['subtract', 'divide']:
            out = compute_peak_height(tfm, 0, spacing, op)
            assert isinstance(out, float)
