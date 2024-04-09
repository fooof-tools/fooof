"""Tests for the specparam.data.utils."""

from copy import deepcopy

import numpy as np

from specparam.data.utils import *

###################################################################################################
###################################################################################################

def test_get_model_params(tresults):

    for dname in ['aperiodic_params', 'aperiodic', 'peak_params', 'peak',
                  'error', 'r_squared', 'gaussian_params', 'gaussian']:
        assert np.any(get_model_params(tresults, dname))

    if dname == 'aperiodic_params' or dname == 'aperiodic':
        for dtype in ['offset', 'exponent']:
            assert np.any(get_model_params(tresults, dname, dtype))

    if dname == 'peak_params' or dname == 'peak':
        for dtype in ['CF', 'PW', 'BW']:
            assert np.any(get_model_params(tresults, dname, dtype))

def test_get_group_params(tresults):

    gresults = [tresults, tresults]

    for dname in ['aperiodic_params', 'peak_params', 'error', 'r_squared', 'gaussian_params']:
        assert np.any(get_group_params(gresults, dname))

    if dname == 'aperiodic_params':
        for dtype in ['offset', 'exponent']:
            assert np.any(get_group_params(gresults, dname, dtype))

    if dname == 'peak_params':
        for dtype in ['CF', 'PW', 'BW']:
            assert np.any(get_group_params(gresults, dname, dtype))

def test_get_periodic_labels():

    keys = ['cf', 'pw', 'bw']

    tdict1 = {
        'offset' : [1, 1],
        'exponent' : [1, 1],
        'error' : [1, 1],
        'r_squared' : [1, 1],
    }

    out1 = get_periodic_labels(tdict1)
    assert isinstance(out1, dict)
    for key in keys:
        assert key in out1
        assert len(out1[key]) == 0

    tdict2 = deepcopy(tdict1)
    tdict2.update({
        'cf_0' : [1, 1],
        'pw_0' : [1, 1],
        'bw_0' : [1, 1],
    })
    out2 = get_periodic_labels(tdict2)
    for key in keys:
        assert len(out2[key]) == 1
        for el in out2[key]:
            assert key in el

    tdict3 = deepcopy(tdict1)
    tdict3.update({
        'alpha_cf' : [1, 1],
        'alpha_pw' : [1, 1],
        'alpha_bw' : [1, 1],
        'beta_cf' : [1, 1],
        'beta_pw' : [1, 1],
        'beta_bw' : [1, 1],
    })
    out3 = get_periodic_labels(tdict3)
    for key in keys:
        assert len(out3[key]) == 2
        for el in out3[key]:
            assert key in el

def test_get_band_labels():

    tdict1 = {
        'offset' : [0, 1],
        'exponent' : [0, 1],
        'error' : [0, 1],
        'r_squared' : [0, 1],
        'alpha_cf' : [0, 1],
        'alpha_pw' : [0, 1],
        'alpha_bw' : [0, 1],
    }

    band_labels1 = get_band_labels(tdict1)
    assert band_labels1 == ['alpha']

    tdict2 = {'cf': ['alpha_cf', 'beta_cf'],
              'pw': ['alpha_pw', 'beta_pw'],
              'bw': ['alpha_bw', 'beta_bw']}

    band_labels2 = get_band_labels(tdict2)
    assert band_labels2 == ['alpha', 'beta']

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
