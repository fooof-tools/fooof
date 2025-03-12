"""Tests for specparam.objs.algorthm, including the base object and it's methods."""

from specparam.objs.base import BaseObject
from specparam.sim import sim_power_spectrum

from specparam.tests.tdata import default_spectrum_params

from specparam.objs.algorithm import *

###################################################################################################
###################################################################################################

## Algorithm Object

def test_algorithm_inherit():

    class TestAlgo(SpectralFitAlgorithm, BaseObject):
        def __init__(self):
            BaseObject.__init__(self, aperiodic_mode='fixed', periodic_mode='gaussian')
            SpectralFitAlgorithm.__init__(self)

    talgo = TestAlgo()
    talgo.fit(*sim_power_spectrum(*default_spectrum_params()))
