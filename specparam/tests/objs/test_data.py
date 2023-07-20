"""Tests for specparam.objs.data, including the data object and it's methods."""

from specparam.objs.data import *

###################################################################################################
###################################################################################################

def test_base_object():
    """Check base object initializes properly."""

    assert BaseData()

def test_base_add_data():

    tbase = BaseData()
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])
    tbase.add_data(freqs, pows)
