"""Tests for the specparam.data.utils."""

from copy import deepcopy

import numpy as np

from specparam.data.utils import *

###################################################################################################
###################################################################################################

def test_get_model_params(tresults, tmodes):

    for dname in ['aperiodic_params', 'aperiodic',
                  'peak_params', 'peak',
                  'gaussian_params', 'gaussian',
                  'error_mae', 'gof_rsquared']:
        assert np.any(get_model_params(tresults, tmodes, dname))

    if dname == 'aperiodic_params' or dname == 'aperiodic':
        for dtype in ['offset', 'exponent']:
            assert np.any(get_model_params(tresults, tmodes, dname, dtype))

    if dname == 'peak_params' or dname == 'peak':
        for dtype in ['CF', 'PW', 'BW']:
            assert np.any(get_model_params(tresults, tmodes, dname, dtype))

def test_get_group_params(tresults, tmodes):

    gresults = [tresults, tresults]

    for dname in ['aperiodic_params', 'peak_params', 'gaussian_params',
                  'error_mae', 'gof_rsquared',]:
        assert np.any(get_group_params(gresults, tmodes, dname))

    if dname == 'aperiodic_params':
        for dtype in ['offset', 'exponent']:
            assert np.any(get_group_params(gresults, tmodes, dname, dtype))

    if dname == 'peak_params':
        for dtype in ['CF', 'PW', 'BW']:
            assert np.any(get_group_params(gresults, tmodes, dname, dtype))

def test_get_results_by_ind():

    tdict = {
        'offset' : [0, 1],
        'exponent' : [0, 1],
        'error' : [0, 1],
        'r_squared' : [0, 1],
        'alpha_cf' : [0, 1],
        'alpha_pw' : [0, 1],
        'alpha_bw' : [0, 1],
    }

    ind = 0
    out0 = get_results_by_ind(tdict, ind)
    assert isinstance(out0, dict)
    for key in tdict.keys():
        assert key in out0.keys()
        assert out0[key] == tdict[key][ind]

    ind = 1
    out1 = get_results_by_ind(tdict, ind)
    for key in tdict.keys():
        assert out1[key] == tdict[key][ind]


def test_get_results_by_row():

    tdict = {
        'offset' : np.array([[0, 1], [2, 3]]),
        'exponent' : np.array([[0, 1], [2, 3]]),
        'error' : np.array([[0, 1], [2, 3]]),
        'r_squared' : np.array([[0, 1], [2, 3]]),
        'alpha_cf' : np.array([[0, 1], [2, 3]]),
        'alpha_pw' : np.array([[0, 1], [2, 3]]),
        'alpha_bw' : np.array([[0, 1], [2, 3]]),
    }

    ind = 0
    out0 = get_results_by_row(tdict, ind)
    assert isinstance(out0, dict)
    for key in tdict.keys():
        assert key in out0.keys()
        assert np.array_equal(out0[key], tdict[key][ind])

    ind = 1
    out1 = get_results_by_row(tdict, ind)
    for key in tdict.keys():
        assert np.array_equal(out1[key], tdict[key][ind])

def test_flatten_results_dict():

    tdict = {
        'offset' : np.array([[0, 1], [2, 3]]),
        'exponent' : np.array([[0, 1], [2, 3]]),
        'error' : np.array([[0, 1], [2, 3]]),
        'r_squared' : np.array([[0, 1], [2, 3]]),
        'alpha_cf' : np.array([[0, 1], [2, 3]]),
        'alpha_pw' : np.array([[0, 1], [2, 3]]),
        'alpha_bw' : np.array([[0, 1], [2, 3]]),
    }

    out = flatten_results_dict(tdict)

    assert np.array_equal(out['event'], np.array([0, 0, 1, 1]))
    assert np.array_equal(out['window'], np.array([0, 1, 0, 1]))
    for key, values in out.items():
        assert values.ndim == 1
        if key not in ['event', 'window']:
            assert np.array_equal(values, np.array([0, 1, 2, 3]))
