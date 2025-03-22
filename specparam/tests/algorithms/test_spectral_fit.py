"""Tests for specparam.algorthms.spectral_fit."""

from specparam.modes.modes import Modes
from specparam.objs.base import BaseObject
from specparam.sim import sim_power_spectrum
from specparam.algorithms.algorithm import AlgorithmDefinition

from specparam.tests.tdata import default_spectrum_params

from specparam.algorithms.spectral_fit import *

###################################################################################################
###################################################################################################

def test_algorithm_inherit():

    class TestAlgo(SpectralFitAlgorithm, BaseObject):
        def __init__(self):
            self.modes = Modes(aperiodic='fixed', periodic='gaussian')
            BaseObject.__init__(self)
            SpectralFitAlgorithm.__init__(self)

    talgo = TestAlgo()
    assert isinstance(talgo.algorithm, AlgorithmDefinition)
    talgo.fit(*sim_power_spectrum(*default_spectrum_params()))
