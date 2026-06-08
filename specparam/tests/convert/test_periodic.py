"""Test functions for specparam.convert.periodic."""

from specparam.convert.periodic import *

###################################################################################################
###################################################################################################

def test_compute_fwhm():

    assert compute_fwhm(1.5)

def test_compute_gauss_std():

    assert compute_gauss_std(1.0)

def test_compute_peak_height(tfm):

    for spacing in ['log', 'linear']:
        for op in ['subtract', 'divide']:
            out = compute_peak_height(tfm, 0, spacing, op)
            assert isinstance(out, float)
