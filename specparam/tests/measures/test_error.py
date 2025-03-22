"""Test functions for specparam.measures.error."""

import numpy as np

from specparam.measures.error import *

###################################################################################################
###################################################################################################

def test_compute_mean_abs_error(tfm):

    error = compute_mean_abs_error(tfm.data.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_mean_squared_error(tfm):

    error = compute_mean_squared_error(tfm.data.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_root_mean_squared_error(tfm):

    error = compute_root_mean_squared_error(tfm.data.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_median_abs_error(tfm):

    error = compute_median_abs_error(tfm.data.power_spectrum, tfm.modeled_spectrum_)
    assert isinstance(error, float)

def test_compute_error(tfm):

    for metric in ['mae', 'mse', 'rmse', 'medae']:
        error = compute_error(tfm.data.power_spectrum, tfm.modeled_spectrum_)
        assert isinstance(error, float)
