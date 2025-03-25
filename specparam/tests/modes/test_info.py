"""Tests for specparam.modes.info."""

from specparam.modes.info import *

###################################################################################################
###################################################################################################

def test_get_peak_indices():

    indices = get_peak_indices()

    # Check it returns a valid object & that values are correct
    assert indices
    for ind, val in enumerate(['CF', 'PW', 'BW']):
        assert indices[val] == ind

def test_get_ap_indices():

    indices_fixed = get_indices('fixed')

    assert indices_fixed
    for ind, val in enumerate(['offset', 'exponent']):
        assert indices_fixed[val] == ind

    indices_knee = get_indices('knee')

    assert indices_knee
    for ind, val in enumerate(['offset', 'knee', 'exponent']):
        assert indices_knee[val] == ind

def test_get_indices():

    all_indices_fixed = get_indices('fixed')
    assert len(all_indices_fixed) == 5

    all_indices_knee = get_indices('knee')
    assert len(all_indices_knee) == 6
