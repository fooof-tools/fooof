"""Tests for specparam.modes.modes."""

from specparam.modes.definitions import AP_MODES, PE_MODES
from specparam.modes.modes import *

###################################################################################################
###################################################################################################

def test_modes():

    modes = Modes(aperiodic='fixed', periodic='gaussian')
    assert modes
    assert isinstance(modes.aperiodic, Mode)
    assert isinstance(modes.periodic, Mode)

def test_check_mode_definition():

    for ap_mode in AP_MODES.keys():
        mode = check_mode_definition(ap_mode, AP_MODES)
        assert isinstance(mode, Mode)

    for pe_mode in PE_MODES.keys():
        mode = check_mode_definition(pe_mode, PE_MODES)
        assert isinstance(mode, Mode)
