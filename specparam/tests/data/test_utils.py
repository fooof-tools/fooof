"""Tests for the specparam.data.utils."""

import numpy as np

from specparam.data.utils import *

###################################################################################################
###################################################################################################

def test_get_model_params(tresults, tmodes):

    for component in tmodes.components:

        assert np.any(get_model_params(tresults, tmodes, component))

        for param in getattr(tmodes, component).params.labels:

            assert np.any(get_model_params(tresults, tmodes, component, param))

def test_get_group_params(tresults, tmodes):

    gresults = [tresults, tresults]

    for component in tmodes.components:

        assert np.any(get_group_params(gresults, tmodes, component))

        for param in getattr(tmodes, component).params.labels:

            assert np.any(get_group_params(gresults, tmodes, component, param))

def test_get_group_metrics(tresults):

    gresults = [tresults, tresults]
    measures = {'error' : 'mae', 'gof' : 'rsquared'}

    for metric in measures.keys():

        out1 = get_group_metrics(gresults, metric)
        assert np.all(out1)
        assert len(out1) == len(gresults)

        out2 = get_group_metrics(gresults, metric, measures[metric])
        assert np.all(out2)
        assert len(out2) == len(gresults)

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
