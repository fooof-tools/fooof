"""Test functions for fooof.sim.gen"""

import numpy as np
from numpy import array_equal

from fooof.tests.tutils import default_group_params

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
    pe_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum(freq_range, ap_params, pe_params)

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

    # Test with a rotation applied returned
    f_rotation = 20
    xs, ys = gen_power_spectrum(freq_range, ap_params, pe_params, f_rotation=f_rotation)

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

def test_gen_power_spectrum_return_params():

    freq_range = [3, 50]
    ap_params = [50, 2]
    pe_params = [[10, 0.5, 2], [20, 0.3, 4]]
    nlv = 0.01

    xs, ys, sp = gen_power_spectrum(freq_range, ap_params, pe_params,
                                    nlv, return_params=True)

    # Test returning parameters
    assert array_equal(sp.aperiodic_params, ap_params)
    assert array_equal(sp.periodic_params, pe_params)
    assert sp.nlv == nlv

def test_gen_group_power_spectra():

    n_spectra = 3

    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params())

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == 2
    assert ys.shape[0] == n_spectra

    # Test the case in which periodic params are an empty list
    xs, ys = gen_group_power_spectra(2, [3, 50], [1, 1], [])

    assert np.all(xs)
    assert np.all(ys)

    # Test with a rotation applied returned
    f_rotation = 20
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params(), f_rotation=f_rotation)

    assert np.all(xs)
    assert np.all(ys)

def test_gen_group_power_spectra_return_params():

    n_spectra = 3

    aps = [1, 1]
    pes = [10, 0.5, 1]
    nlv = 0.01

    xs, ys, sim_params = gen_group_power_spectra(n_spectra, [1, 50], aps, pes, nlv,
                                                 return_params=True)

    assert n_spectra == ys.shape[0] == len(sim_params)
    sp = sim_params[0]
    assert array_equal(sp.aperiodic_params, aps)
    assert array_equal(sp.periodic_params, [pes])
    assert sp.nlv == nlv

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

def test_gen_periodic():

    xs = gen_freqs([3, 50], 0.5)
    pe_params = [10, 2, 1]

    pe_vals = gen_periodic(xs, pe_params)

    assert np.all(np.invert(np.isnan(pe_vals)))
    assert xs[np.argmax(pe_vals)] == 10

def test_gen_noise():

    xs = gen_freqs([3, 50], 0.5)

    nlv = 0.1
    noise = gen_noise(xs, nlv)
    assert np.all(np.invert(np.isnan(noise)))
    assert np.isclose(np.std(noise), nlv, 0.25)

    nlv = 0.5
    noise = gen_noise(xs, nlv)
    assert np.all(np.invert(np.isnan(noise)))
    assert np.isclose(np.std(noise), nlv, 0.25)

def test_gen_power_values():

    xs = gen_freqs([3, 50], 0.5)

    ap_params = [50, 2]
    pe_params = [10, 2, 1]
    nlv = 0.1

    ys = gen_power_vals(xs, ap_params, pe_params, nlv)

    assert np.all(ys)

def test_gen_rotated_power_vals():

    xs = gen_freqs([3, 50], 0.5)

    ap_params = [50, 2]
    pe_params = [10, 2, 1]
    nlv = 0.1
    f_rotation = 12

    ys = gen_rotated_power_vals(xs, ap_params, pe_params, nlv, f_rotation)

    assert np.all(ys)

def test_gen_model():

    xs = gen_freqs([3, 50], 0.5)
    ys = gen_model(xs, np.array([1, 1]), np.array([10, 0.5, 1]))

    assert np.all(ys)
