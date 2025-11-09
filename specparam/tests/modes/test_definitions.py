"""Tests for specparam.modes.definitions."""

from specparam.modes.definitions import *

###################################################################################################
###################################################################################################

def test_check_modes():

    check_modes('aperiodic')
    check_modes('periodic')

def test_check_mode_definition():

    for ap_mode in AP_MODES.keys():
        mode = check_mode_definition(ap_mode, AP_MODES)
        assert isinstance(mode, Mode)

    for pe_mode in PE_MODES.keys():
        mode = check_mode_definition(pe_mode, PE_MODES)
        assert isinstance(mode, Mode)
