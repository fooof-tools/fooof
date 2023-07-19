"""Tests for specparam.objs.base, including the base object and it's methods."""

from specparam.sim import sim_power_spectrum

from specparam.objs.base import *

###################################################################################################
###################################################################################################

def test_base_object():
    """Check base object initializes properly."""

    assert BaseSpectralModel()

def test_base_add_data():

    tbase = BaseSpectralModel()
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])
    tbase.add_data(freqs, pows)

def test_base_fit():

    tbase = BaseSpectralModel()
    tbase.fit(*sim_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))
