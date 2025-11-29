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

def test_check_converters():

    check_converters('aperiodic')
    check_converters('periodic')
