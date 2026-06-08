"""Test functions for specparam.modes.check."""

from specparam.modes.check import *

###################################################################################################
###################################################################################################

def test_check_modes():

    check_modes('aperiodic', True)
    check_modes('periodic', True)
