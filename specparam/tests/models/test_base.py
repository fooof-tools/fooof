"""Tests for specparam.models.base."""

from specparam.models.base import *

###################################################################################################
###################################################################################################

def test_base_model():

    tbase = BaseModel(aperiodic_mode='fixed', periodic_mode='gaussian',
                      converters=None, verbose=False)
    assert isinstance(tbase, BaseModel)

def test_common_base_copy():

    tbase = BaseModel(aperiodic_mode='fixed', periodic_mode='gaussian',
                      converters=None, verbose=False)
    ntbase = tbase.copy()

    assert ntbase != tbase
