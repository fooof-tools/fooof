"""Tests for specparam.results.params."""

import numpy as np

from specparam.results.params import *

###################################################################################################
###################################################################################################

## ComponentParameters object

def test_component_parameters_str():

    # Test basic string definition
    acp = ComponentParameters('aperiodic')
    assert acp

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

def test_component_parameters_modes(tmodes):

    ## Check aperiodic mode component definition
    ap_params = ComponentParameters(tmodes.aperiodic)
    assert ap_params._fit.ndim == tmodes.aperiodic.ndim
    assert ap_params._fit.size == ap_params._converted.size == tmodes.aperiodic.params.n_params
    assert ap_params.indices == tmodes.aperiodic.params.indices
    assert ap_params.ndim == tmodes.aperiodic.ndim

    ## Check periodic mode component definition
    pe_params = ComponentParameters(tmodes.periodic)
    assert pe_params._fit.ndim == tmodes.periodic.ndim
    assert pe_params._fit.size == pe_params._converted.size == tmodes.periodic.params.n_params
    assert pe_params.indices == tmodes.periodic.params.indices
    assert pe_params.ndim == tmodes.periodic.ndim

## ModelParameters object

def test_model_parameters():

    mp = ModelParameters()
    assert mp

    assert isinstance(mp.aperiodic, ComponentParameters)
    assert isinstance(mp.periodic, ComponentParameters)
