"""Tests for fooof.core.info."""

from fooof.core.info import *

###################################################################################################
###################################################################################################

def test_get_description(tfm):

    desc =  get_description()
    objs = dir(tfm)

    # Test that everything in dict is a valid component of the fooof object
    for ke, va in desc.items():
        for it in va:
            assert it in objs

def test_get_indices():

    indices_fixed = get_indices('fixed')
    assert indices_fixed
    for ke, va in indices_fixed.items():
        if ke == 'knee':
            assert not va
        else:
            assert isinstance(va, int)

    indices_knee = get_indices('knee')
    assert indices_knee
    for ke, va in indices_knee.items():
        assert isinstance(va, int)
