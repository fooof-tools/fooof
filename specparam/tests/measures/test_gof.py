"""Test functions for specparam.measures.gof."""

import numpy as np

from specparam.measures.gof import *

###################################################################################################
###################################################################################################

## GOF FUNCTIONS

def test_compute_r_squared(tfm):

    r_squared = compute_r_squared(tfm.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(r_squared, float)

def test_compute_adj_r_squared(tfm):

    r_squared = compute_adj_r_squared(tfm.power_spectrum, tfm.modeled_spectrum_, 5)
    assert isinstance(r_squared, float)

## ERROR FUNCTIONS

def test_compute_mean_abs_error(tfm):

    error = compute_mean_abs_error(tfm.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_mean_squared_error(tfm):

    error = compute_mean_squared_error(tfm.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_root_mean_squared_error(tfm):

    error = compute_root_mean_squared_error(tfm.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_median_abs_error(tfm):

    error = compute_median_abs_error(tfm.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_error(tfm):

    for metric in ['mae', 'mse', 'rmse', 'medae']:
        error = compute_error(tfm.power_spectrum, tfm.modeled_spectrum_)
        assert isinstance(error, float)
