"""Test functions for FOOOF utils."""

import numpy as np

from fooof.utils import *

###################################################################################################
###################################################################################################

def test_trim_psd():

    f_in = np.array([0., 1., 2., 3., 4., 5.])
    p_in = np.array([1., 2., 3., 4., 5., 6.])

    f_out, p_out = trim_psd(f_in, p_in, [2., 4.])

    assert np.array_equal(f_out, np.array([2., 3., 4.]))
    assert np.array_equal(p_out, np.array([3., 4., 5.]))

def test_mk_freq_vector():

    f_range = [3, 40]
    f_res = 0.5

    freqs = mk_freq_vector(f_range, f_res)

    assert freqs.min() == f_range[0]
    assert freqs.max() == f_range[1]
    assert np.mean(np.diff(freqs)) == f_res
