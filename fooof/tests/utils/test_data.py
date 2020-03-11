"""Test functions for fooof.utils.data."""

import numpy as np

from fooof.utils.data import *

###################################################################################################
###################################################################################################

def test_trim_spectrum():

    f_in = np.array([0., 1., 2., 3., 4., 5.])
    p_in = np.array([1., 2., 3., 4., 5., 6.])

    f_out, p_out = trim_spectrum(f_in, p_in, [2., 4.])

    assert np.array_equal(f_out, np.array([2., 3., 4.]))
    assert np.array_equal(p_out, np.array([3., 4., 5.]))

def test_compute_pointwise_error():

    d1 = np.ones(5) * 2
    d2 = np.ones(5)

    errs = compute_pointwise_error(d1, d2)
    assert np.array_equal(errs, np.array([1, 1, 1, 1, 1]))
