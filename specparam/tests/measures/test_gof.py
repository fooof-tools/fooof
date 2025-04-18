"""Test functions for specparam.measures.gof."""

from specparam.measures.gof import *

###################################################################################################
###################################################################################################

def test_compute_r_squared(tfm):

    r_squared = compute_r_squared(tfm.data.power_spectrum, tfm.results.modeled_spectrum_)
    assert isinstance(r_squared, float)

def test_compute_adj_r_squared(tfm):

    r_squared = compute_adj_r_squared(tfm.data.power_spectrum, tfm.results.modeled_spectrum_, 5)
    assert isinstance(r_squared, float)

def test_compute_gof(tfm):

    for metric in ['r_squared', 'adj_r_squared']:
        gof = compute_gof(tfm.data.power_spectrum, tfm.results.modeled_spectrum_)
        assert isinstance(gof, float)
