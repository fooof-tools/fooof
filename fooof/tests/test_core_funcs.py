"""Tests for FOOOF core.funcs."""

from py.test import raises

import numpy as np
from scipy.stats import norm, linregress

from fooof.core.funcs import *

###################################################################################################
###################################################################################################

def test_gaussian_function():

    ctr, amp, wid = 50, 5, 10

    xs = np.arange(1, 100)
    ys = gaussian_function(xs, ctr, amp, wid)

    assert np.all(ys)

    # Check distribution matches generated gaussian from scipy
    #  Generated gaussian is normalized for this comparison, amp tested separately
    assert max(ys) == amp
    assert np.allclose([i/sum(ys) for i in ys], norm.pdf(xs, ctr, wid))

def test_expo_function():

    off, knee, exp = 10, 5, 2

    xs = np.arange(1, 100)
    ys = expo_function(xs, off, knee, exp)

    assert np.all(ys)

    # Note: no obvious way to test the knee specifically
    #  Here - test that past the knee, has expected slope & offset value
    exp_meas, off_meas, _, _, _ = linregress(np.log10(xs[knee**2:]), ys[knee**2:])

    assert np.isclose(off_meas, off, 0.1)
    assert np.isclose(np.abs(exp_meas), exp, 0.1)

def test_expo_nk_function():

    off, exp = 10, 2

    xs = np.arange(1, 100)
    ys = expo_nk_function(xs, off, exp)

    assert np.all(ys)

    # By design, this expo function assumes log-space ys, linear xs
    #   Where the log-log should be a straight line. Use that to test.
    sl_meas, off_meas, _, _, _ = linregress(np.log10(xs), ys)

    assert np.isclose(off, off_meas)
    assert np.isclose(exp, np.abs(sl_meas))

def test_linear_function():

    off, sl = 10, 2

    xs = np.arange(1, 100)
    ys = linear_function(xs, off, sl)

    assert np.all(ys)

    sl_meas, off_meas, _, _, _ = linregress(xs, ys)

    assert np.isclose(off_meas, off)
    assert np.isclose(sl_meas, sl)

def test_quadratic_function():

    off, sl, curve = 10, 3, 2

    xs = np.arange(1, 100)
    ys = quadratic_function(xs, off, sl, curve)

    assert np.all(ys)

    curve_meas, sl_meas, off_meas = np.polyfit(xs, ys, 2)

    assert np.isclose(off_meas, off)
    assert np.isclose(sl_meas, sl)
    assert np.isclose(curve_meas, curve)

def test_get_bg_func():

    bgf_nk = get_bg_func('fixed')
    assert bgf_nk

    bgf_kn = get_bg_func('knee')
    assert bgf_kn

    # Check error
    with raises(ValueError):
        get_bg_func('bad')

def test_infer_bg_func():

    bgp_nk = [50, 1]
    bgm_nk = infer_bg_func(bgp_nk)
    assert bgm_nk == 'fixed'

    bgp_kn = [50, 2, 1]
    bgm_kn = infer_bg_func(bgp_kn)
    assert bgm_kn == 'knee'

    # Check error
    with raises(ValueError):
        infer_bg_func([1, 2, 3, 4])
