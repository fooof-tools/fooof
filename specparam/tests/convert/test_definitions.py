"""Test functions for specparam.convert.definitions."""

from specparam.modes.mode import VALID_COMPONENTS
from specparam.convert.converter import BaseParamConverter

from specparam.convert.definitions import *

###################################################################################################
###################################################################################################

def test_converters_library():

    for component in VALID_COMPONENTS:
        for parameter, converters in CONVERTERS[component].items():
            for label, converter in converters.items():
                assert isinstance(converter, BaseParamConverter)
                assert converter.component == component
                assert converter.name == label
                assert callable(converter.function)

def test_update_converters():

    converters1 = {'aperiodic' : {'exponent' : 'custom'}}
    out1 = update_converters(DEFAULT_CONVERTERS, converters1)
    assert out1['periodic'] == DEFAULT_CONVERTERS['periodic']
    assert out1['aperiodic']['exponent'] == converters1['aperiodic']['exponent']

    converters2 = {'periodic' : {'cf' : 'custom'}}
    out2 = update_converters(DEFAULT_CONVERTERS, converters2)
    assert out2['aperiodic'] == DEFAULT_CONVERTERS['aperiodic']
    assert out2['periodic']['cf'] == converters2['periodic']['cf']

    converters3 = {'aperiodic' : {'knee' : 'custom'}}
    out3 = update_converters(DEFAULT_CONVERTERS, converters3)
    assert out3['periodic'] == DEFAULT_CONVERTERS['periodic']
    assert out3['aperiodic']['knee'] == converters3['aperiodic']['knee']

def test_check_converters():

    check_converters('aperiodic')
    check_converters('periodic')
