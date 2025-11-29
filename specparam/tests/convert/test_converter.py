"""Test functions for specparam.convert.converter."""

from specparam.convert.converter import *

###################################################################################################
###################################################################################################

def test_base_param_converter():

    baconv = BaseParamConverter('tcomponent', 'tparameter', 'tname', 'tdescription', lambda a : a)
    assert baconv

def test_aperiodic_param_converter():

    apconv = AperiodicParamConverter('tparameter', 'tname', 'tdescription',
                                     lambda param, model : param)
    assert apconv
    assert apconv.component == 'aperiodic'
    assert apconv(1, None) == 1

def test_periodic_param_converter():

    peconv = PeriodicParamConverter('tparameter', 'tname', 'tdescription',
                                    lambda param, model, peak_ind : param)
    assert peconv
    assert peconv.component == 'periodic'
    assert peconv(1, None, None) == 1
