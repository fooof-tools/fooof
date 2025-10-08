"""Test functions for specparam.measures.estimates."""

from specparam.sim.gen import gen_freqs, gen_noise
from specparam.modes.funcs import gaussian_function
from specparam.measures.params import compute_fwhm

from specparam.measures.estimates import *

###################################################################################################
###################################################################################################

def test_estimate_fwhm():

    fres = 0.1
    freqs = gen_freqs([1, 40], fres)
    gauss_params = [10, 1, 2]
    peak = gaussian_function(freqs, *gauss_params) + gen_noise(freqs, 0.01)

    out = estimate_fwhm(peak, np.argmax(peak), fres)
    assert isinstance(out, float)
    assert np.isclose(out, compute_fwhm(gauss_params[2]), atol=0.5)
