"""Test functions for fooof.utils.data."""

import numpy as np

from fooof.sim.gen import gen_power_spectrum

from fooof.utils.data import *

###################################################################################################
###################################################################################################

def test_trim_spectrum():

    f_in = np.array([0., 1., 2., 3., 4., 5.])
    p_in = np.array([1., 2., 3., 4., 5., 6.])

    f_out, p_out = trim_spectrum(f_in, p_in, [2., 4.])

    assert np.array_equal(f_out, np.array([2., 3., 4.]))
    assert np.array_equal(p_out, np.array([3., 4., 5.]))

def test_interpolate_spectrum():

    freqs, powers = gen_power_spectrum(\
        [1, 75], [1, 1], [[10, 0.5, 1.0], [60, 2, 0.1]])

    freqs_out, powers_out = interpolate_spectrum(freqs, powers, [58, 62])

    assert np.array_equal(freqs, freqs_out)
    assert np.all(powers)
    assert powers.shape == powers_out.shape
