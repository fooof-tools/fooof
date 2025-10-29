"""Tests for specparam.modes.definitions."""

from specparam.modes.definitions import *

###################################################################################################
###################################################################################################

def test_check_modes():

    check_modes('aperiodic')
    check_modes('periodic')
