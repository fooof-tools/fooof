"""Tests for specparam.objs.params."""

import numpy as np

from specparam.objs.params import *

###################################################################################################
###################################################################################################

## ComponentParameters object

def test_component_parameters():

    acp = ComponentParameters('aperiodic')
    assert acp

    # Check reseting parameter stores
    acp.reset(2)
    assert len(acp._fit) == 2
    assert len(acp._converted) == 2

    # Check adding values
    fparams = np.array([1, 2])
    acp.add_params('fit', fparams)
    assert acp.has_fit
    assert np.array_equal(acp.params, fparams)

    cparams = np.array([3, 4])
    acp.add_params('converted', cparams)
    assert acp.has_converted
    assert np.array_equal(acp.params, cparams)

    # Check dictionary export
    pdict = acp.asdict()
    assert isinstance(pdict, dict)
    assert np.array_equal(pdict['aperiodic_fit'], fparams)
    assert np.array_equal(pdict['aperiodic_converted'], cparams)

## ModelParameters object

def test_model_parameters():

    mp = ModelParameters()
    assert mp

    assert isinstance(mp.aperiodic, ComponentParameters)
    assert isinstance(mp.peak, ComponentParameters)
