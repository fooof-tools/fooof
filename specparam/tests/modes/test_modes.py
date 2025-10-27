"""Tests for specparam.modes.modes."""

from specparam.data import ModelModes
from specparam.modes.definitions import AP_MODES, PE_MODES

from specparam.modes.modes import *

###################################################################################################
###################################################################################################

def test_modes():

    modes = Modes(aperiodic='fixed', periodic='gaussian')
    assert modes
    assert isinstance(modes.aperiodic, Mode)
    assert isinstance(modes.periodic, Mode)
    modes.check_params()

def test_modes_get_modes():

    ap_mode_name = 'fixed'
    pe_mode_name = 'gaussian'

    modes = Modes(aperiodic=ap_mode_name, periodic=pe_mode_name)
    mode_names = modes.get_modes()
    assert isinstance(mode_names, ModelModes)
    assert mode_names.aperiodic_mode == ap_mode_name
    assert mode_names.periodic_mode == pe_mode_name

def test_check_mode_definition():

    for ap_mode in AP_MODES.keys():
        mode = check_mode_definition(ap_mode, AP_MODES)
        assert isinstance(mode, Mode)

    for pe_mode in PE_MODES.keys():
        mode = check_mode_definition(pe_mode, PE_MODES)
        assert isinstance(mode, Mode)
