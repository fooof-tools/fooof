"""Test functions for specparam.params.check."""

from specparam.params.check import *

###################################################################################################
###################################################################################################

def test_check_converters():

    check_converters('aperiodic')
    check_converters('periodic')
