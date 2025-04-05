"""Tests for specparam.modes.info."""

from specparam.modes.info import *

###################################################################################################
###################################################################################################

def test_get_indices():

    all_indices_fixed = get_indices('fixed')
    assert len(all_indices_fixed) == 5

    all_indices_knee = get_indices('knee')
    assert len(all_indices_knee) == 6
