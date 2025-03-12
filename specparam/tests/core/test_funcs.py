"""Tests for specparam.core.funcs."""

from pytest import raises

import numpy as np
from scipy.stats import norm, linregress

from specparam.modutils.errors import InconsistentDataError

from specparam.core.funcs import *

###################################################################################################
###################################################################################################

## Periodic functions

def test_gaussian_function():

    ctr, hgt, wid = 50, 5, 10

    xs = np.arange(1, 100)
    ys = gaussian_function(xs, ctr, hgt, wid)

    assert np.all(ys)

    # Check distribution matches generated gaussian from scipy
    #  Generated gaussian is normalized for this comparison, height tested separately
    assert max(ys) == hgt
    assert np.allclose([ii/sum(ys) for ii in ys], norm.pdf(xs, ctr, wid))

def test_skewnorm_function():

    # Check that with no skew, approximate gaussian
    ctr, hgt, wid, skew = 50, 5, 10, 1
    xs = np.arange(1, 100)
    ys_gaus = gaussian_function(xs, ctr, hgt, wid)
    ys_skew = skewnorm_function(xs, ctr, hgt, wid, skew)
    np.allclose(ys_gaus, ys_skew, atol=0.001)

    # Check with some skew - right skew (more density after center)
    skew1 = 2
    ys_skew1 = skewnorm_function(xs, ctr, hgt, wid, skew1)
    assert sum(ys_skew1[xs<ctr]) < sum(ys_skew1[xs>ctr])

    # Check with some skew - left skew (more density before center)
    skew2 = -2
    ys_skew2 = skewnorm_function(xs, ctr, hgt, wid, skew2)
    assert sum(ys_skew2[xs<ctr]) > sum(ys_skew2[xs>ctr])

def test_cauchy_function():

    ctr, hgt, wid = 50, 5, 10

    xs = np.arange(1, 100)
    ys = cauchy_function(xs, ctr, hgt, wid)

    assert np.all(ys)

## Aperiodic functions

def test_expo_function():

    off, knee, exp = 10, 5, 2

    xs = np.arange(1, 100)
    ys = expo_function(xs, off, knee, exp)

    assert np.all(ys)

    # Note: no obvious way to test the knee specifically
    #  Here - test that past the knee, has expected exponent & offset value
    exp_meas, off_meas, _, _, _ = linregress(np.log10(xs[knee**2:]), ys[knee**2:])

    assert np.isclose(off_meas, off, 0.1)
    assert np.isclose(np.abs(exp_meas), exp, 0.1)

def test_expo_nk_function():

    off, exp = 10, 2

    xs = np.arange(1, 100)
    ys = expo_nk_function(xs, off, exp)

    assert np.all(ys)

    # By design, this expo function assumes linear xs and log-space ys
    #   Where the log-log should be a straight line. Use that to test.
    exp_meas, off_meas, _, _, _ = linregress(np.log10(xs), ys)
    assert np.isclose(off, off_meas)
    assert np.isclose(exp, np.abs(exp_meas))

def test_double_expo_function():

    off, exp0, knee, exp1 = 10, 1, 5, 1

    xs = np.arange(0.1, 100, 0.1)
    ys = double_expo_function(xs, off, exp0, knee, exp1)

    assert np.all(ys)

    # Note: no obvious way to test the knee specifically
    #  Here - test that exponents at edges of the psd (pre & post knee) are as expected
    exp_meas0, off_meas0, _, _, _ = linregress(np.log10(xs[:5]), ys[:5])
    assert np.isclose(np.abs(exp_meas0), exp0, 0.1)
    exp_meas1, off_meas1, _, _, _ = linregress(np.log10(xs[-5:]), ys[-5:])
    assert np.isclose(np.abs(exp_meas1), exp0 + exp1, 0.1)
    assert np.isclose(off_meas1, off, 0.25)

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

## Getter functions

def test_get_pe_func():

    pe_ga_func = get_pe_func('gaussian')
    assert callable(pe_ga_func)

    with raises(ValueError):
        get_pe_func('bad')

def test_get_ap_func():

    ap_nk_func = get_ap_func('fixed')
    assert callable(ap_nk_func)

    ap_kn_func = get_ap_func('knee')
    assert callable(ap_kn_func)

    with raises(ValueError):
        get_ap_func('bad')

def test_infer_ap_func():

    ap_nk = [50, 1]
    apf_nk = infer_ap_func(ap_nk)
    assert apf_nk == 'fixed'

    ap_kn = [50, 2, 1]
    apf_kn = infer_ap_func(ap_kn)
    assert apf_kn == 'knee'

    with raises(InconsistentDataError):
        infer_ap_func([1, 2, 3, 4])
