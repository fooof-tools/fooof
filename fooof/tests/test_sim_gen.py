"""Test functions for fooof.sim.gen"""

import numpy as np

from fooof.tests.utils import default_group_params

from fooof.sim.gen import *

###################################################################################################
###################################################################################################

def test_gen_freqs():

    f_range = [3, 40]
    f_res = 0.5

    freqs = gen_freqs(f_range, f_res)

    assert freqs.min() == f_range[0]
    assert freqs.max() == f_range[1]
    assert np.mean(np.diff(freqs)) == f_res

def test_gen_power_spectrum():

    freq_range = [3, 50]
    ap_params = [50, 2]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum(freq_range, ap_params, gaussian_params)

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

def test_gen_group_power_spectra():

    n_spectra = 2

    xs, ys, params = gen_group_power_spectra(n_spectra, *default_group_params())

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == n_spectra

def test_gen_group_power_spectra_empty_gauss():

    n_spectra = 2

    # Test the case in which gaussian params are an empty list
    xs, ys, params = gen_group_power_spectra(2, [3, 50], [1, 1], [])

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == n_spectra

def test_gen_aperiodic():

    xs = gen_freqs([3, 50], 0.5)

    ap_nk = [50, 2]
    apv_nk = gen_aperiodic(xs, ap_nk, 'fixed')
    assert np.all(apv_nk)

    ap_kn = [50, 1, 1]
    apv_kn = gen_aperiodic(xs, ap_kn, 'knee')
    assert np.all(apv_kn)

    # Check without specifying aperiodic mode
    apv_nk_2 = gen_aperiodic(xs, ap_nk)
    assert np.array_equal(apv_nk, apv_nk_2)
    apv_kn_2 = gen_aperiodic(xs, ap_kn)
    assert np.array_equal(apv_kn, apv_kn_2)

def test_gen_peaks():

    xs = gen_freqs([3, 50], 0.5)
    gaussian_params = [10, 2, 1]

    peaks = gen_peaks(xs, gaussian_params)

    assert np.all(np.invert(np.isnan(peaks)))

def test_gen_power_values():

    xs = gen_freqs([3, 50], 0.5)

    ap_params = [50, 2]
    gauss_params = [10, 2, 1]
    nlv = 0.1

    ys = gen_power_vals(xs, ap_params, gauss_params, nlv)

    assert np.all(ys)
