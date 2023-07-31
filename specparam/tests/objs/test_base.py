"""Tests for specparam.objs.base, including the base object and it's methods."""

from specparam.sim import sim_power_spectrum

from specparam.objs.algorithm import SpectralFitAlgorithm

from specparam.objs.base import *

###################################################################################################
###################################################################################################

def test_base_object():

    class TestBase(SpectralFitAlgorithm, BaseObject):
        def __init__(self):
            BaseObject.__init__(self, aperiodic_mode='fixed', periodic_mode='gaussian')
            SpectralFitAlgorithm.__init__(self)

    tbase = TestBase()
    tbase.fit(*sim_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))
