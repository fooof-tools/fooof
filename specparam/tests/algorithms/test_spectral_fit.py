"""Tests for specparam.algorthms.spectral_fit."""

from specparam.modes.modes import Modes
from specparam.models.base import BaseModel
from specparam.objs.data import BaseData
from specparam.objs.results import BaseResults
from specparam.sim import sim_power_spectrum
from specparam.algorithms.algorithm import Algorithm, AlgorithmDefinition

from specparam.tests.tdata import default_spectrum_params

from specparam.algorithms.spectral_fit import *

###################################################################################################
###################################################################################################

def test_algorithm_inherit():

    class TestAlgo(BaseModel):
        def __init__(self):
            BaseModel.__init__(self, verbose=False)
            self.modes = Modes(aperiodic='fixed', periodic='gaussian')
            self.data = BaseData()
            self.add_data = self.data.add_data
            self.results = BaseResults(modes=self.modes)
            self.algorithm = SpectralFitAlgorithm(\
                data=self.data, results=self.results, modes=self.modes)

    talgo = TestAlgo()
    assert isinstance(talgo.algorithm, Algorithm)
    assert isinstance(talgo.algorithm.algorithm, AlgorithmDefinition)
    talgo.fit(*sim_power_spectrum(*default_spectrum_params()))
