"""Test functions for FOOOF synth."""

from collections import Iterable
from itertools import repeat

import numpy as np

from fooof.tests.utils import default_group_params

from fooof.synth import *
from fooof.synth import _check_flat, _check_iter

###################################################################################################
###################################################################################################

def test_param_iter():

    # Test oscillations
    step = Stepper(8, 12, .1)
    osc = [step, .5, .5]
    iter_1 = param_iter(osc)

    for ind, val in enumerate(iter_1):
        assert val == [8 + (.1*ind), .5 , .5]

    # Test background
    step = Stepper(.25, 3, .25)
    bg = [0, step]
    iter_1 = param_iter(bg)

    for ind, val in enumerate(iter_1):
        assert val == [0, .25 + (.25*ind)]

    # Test n oscillations
    step = Stepper(8, 12, .1)
    oscs = [step, .5, .5, 10, .25, 1]
    iter_1 = param_iter(oscs)

    for ind, val in enumerate(iter_1):
        assert val == [8 + (.1*ind), .5 , .5, 10, .25, 1]

    # Test list of lists
    step = Stepper(8, 12, .1)
    osc_1 = [1, 2, 3]
    osc_2 = [4, 5, 6]
    osc_3 = [7, 8, step]
    oscs = [osc_1, osc_2, osc_3]
    iter_2 = param_iter(oscs)

    for ind, val in enumerate(iter_2):
        assert val == [1, 2, 3, 4, 5, 6, 7, 8, 8 + (.1*ind)]


def test_stepper():

    assert Stepper(8,12,.1)


def test_param_sampler():

    pos = [1, 2, 3, 4]
    gen = param_sampler(pos)

    for ind, el in zip(range(3), gen):
        assert el in pos

def test_gen_freqs():

    f_range = [3, 40]
    f_res = 0.5

    freqs = gen_freqs(f_range, f_res)

    assert freqs.min() == f_range[0]
    assert freqs.max() == f_range[1]
    assert np.mean(np.diff(freqs)) == f_res

def test_gen_power_spectrum():

    freq_range = [3, 50]
    bgp = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum(freq_range, bgp, gauss_params)

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

def test_gen_group_power_spectra():

    n_spectra = 2

    xs, ys, params = gen_group_power_spectra(n_spectra, *default_group_params())

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == n_spectra

def test_gen_background():

    xs = gen_freqs([3, 50], 0.5)

    bgp_nk = [50, 2]
    bgv_nk = gen_background(xs, bgp_nk, 'fixed')
    assert np.all(bgv_nk)

    bgp_kn = [50, 1, 1]
    bgv_kn = gen_background(xs, bgp_kn, 'knee')
    assert np.all(bgv_kn)

    # Check without specifying background mode
    bgv_nk_2 = gen_background(xs, bgp_nk)
    assert np.array_equal(bgv_nk, bgv_nk_2)
    bgv_kn_2 = gen_background(xs, bgp_kn)
    assert np.array_equal(bgv_kn, bgv_kn_2)

def test_gen_peaks():

    xs = gen_freqs([3, 50], 0.5)
    gauss_params = [10, 2, 1]

    peaks = gen_peaks(xs, gauss_params)

    assert np.all(np.invert(np.isnan(peaks)))

def test_gen_power_values():

    xs = gen_freqs([3, 50], 0.5)

    bg_params = [50, 2]
    gauss_params = [10, 2, 1]
    nlv = 0.1

    ys = gen_power_vals(xs, bg_params, gauss_params, nlv)

    assert np.all(ys)

def test_rotate_powerlaw():
    # Not the best test right now, just checking that a change in slope of 0
    # does nothing to a flat spectrum.
    freqs = np.arange(500.)

    psd_sim = np.ones_like(freqs)
    psd_rot = rotate_powerlaw(psd_sim, freqs, delta_f=0.)

    assert np.all(psd_rot==psd_sim)

    psd_rot = rotate_powerlaw(psd_sim, freqs, delta_f=0., f_rotation=30.)

    assert np.all(psd_rot==psd_sim)

def test_check_iter():

    # Note: generator case not tested

    # Check that a number input becomes an iterable
    out = _check_iter(12, 3)
    assert isinstance(out, Iterable)
    assert isinstance(out, repeat)

    # Check that single list becomes repeat iterable
    out = _check_iter([1, 1], 2)
    assert isinstance(out, Iterable)
    assert isinstance(out, repeat)

    # Check that a list of lists, of right length stays list of list
    out = _check_iter([[1, 1], [1, 1], [1, 1]], 3)
    assert isinstance(out, Iterable)
    assert isinstance(out, list)
    assert isinstance(out[0], list)

def test_check_flat():

    # Check an empty list stays the same
    assert _check_flat([]) == []

    # Check an already flat list gets left the same
    lst = [1, 2, 3, 4]
    flat_lst = _check_flat(lst)
    assert flat_lst == lst

    # Check a nested list gets flattened
    lst = [[1, 2], [3, 4]]
    flat_lst = _check_flat(lst)
    for el in flat_lst:
        assert isinstance(el, int)
    assert len(flat_lst) == 4
