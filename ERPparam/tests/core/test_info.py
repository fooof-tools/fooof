"""Tests for fooof.core.info."""

from fooof.core.info import *

###################################################################################################
###################################################################################################

def test_get_description(tfm):

    desc = get_description()
    objs = dir(tfm)

    # Test that everything in dict is a valid component of the fooof object
    for ke, va in desc.items():
        for it in va:
            assert it in objs


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

def test_get_info(tfm, tfg):

    for f_obj in [tfm, tfg]:
        assert get_info(f_obj, 'settings')
        assert get_info(f_obj, 'meta_data')
        assert get_info(f_obj, 'results')
