"""Test functions for specparam.sim.gen"""

import numpy as np

from specparam.sim.gen import *

###################################################################################################
###################################################################################################

def test_gen_freqs():

    f_range = [3, 40]
    fs = 0.5

    freqs = gen_freqs(f_range, fs)

    assert freqs.min() == f_range[0]
    assert freqs.max() == f_range[1]
    assert np.mean(np.diff(freqs)) == fs

def test_gen_aperiodic():

    xs = gen_freqs([3, 50], 0.5)

    ap_nk = [50, 2]
    apv_nk = gen_aperiodic(xs, 'fixed', ap_nk)
    assert np.all(apv_nk)

    ap_kn = [50, 1, 1]
    apv_kn = gen_aperiodic(xs, 'knee', ap_kn)
    assert np.all(apv_kn)

def test_gen_periodic():

    xs = gen_freqs([3, 50], 0.5)
    pe_params = [10, 2, 1]

    pe_vals = gen_periodic(xs, 'gaussian', pe_params)

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

    ys = gen_power_vals(xs, 'fixed', ap_params, 'gaussian', pe_params, nlv)

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
    ys = gen_model(xs, 'fixed', np.array([1, 1]), 'gaussian', np.array([10, 0.5, 1]))

    assert np.all(ys)
