"""Tests for specparam.modes.modes."""

from specparam.modes.modes import *

###################################################################################################
###################################################################################################

def test_modes():

    modes = Modes(aperiodic='fixed', periodic='gaussian')
    assert modes
    assert isinstance(modes.aperiodic, Mode)
    assert isinstance(modes.periodic, Mode)
