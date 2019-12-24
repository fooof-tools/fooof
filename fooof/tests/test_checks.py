"""Test functions for fooof.checks."""

import numpy as np

from fooof.checks import *

###################################################################################################
###################################################################################################

def test_compute_pointwise_error():

    d1 = np.ones(5) * 2
    d2 = np.ones(5)

    errs = compute_pointwise_error(d1, d2)
    assert np.array_equal(errs, np.array([1, 1, 1, 1, 1]))

def test_compute_pointwise_error_fm(tfm):

    compute_pointwise_error_fm(tfm, True, True)

def test_compute_pointwise_error_fg(tfg):

    compute_pointwise_error_fg(tfg, True, True)
