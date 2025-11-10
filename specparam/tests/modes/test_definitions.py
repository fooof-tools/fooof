"""Tests for specparam.modes.definitions."""

from specparam.modes.mode import Mode, VALID_COMPONENTS

from specparam.modes.definitions import *

###################################################################################################
###################################################################################################

def test_modes_library():

    for component in VALID_COMPONENTS:
        for key, mode in MODES[component].items():
            assert isinstance(mode, Mode)
            assert mode.name == key

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
