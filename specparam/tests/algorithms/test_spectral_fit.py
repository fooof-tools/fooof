"""Tests for specparam.algorthms.spectral_fit."""

from specparam import SpectralModel
from specparam.models.base import BaseModel
from specparam.objs.data import BaseData
from specparam.objs.results import BaseResults
from specparam.sim import sim_power_spectrum
from specparam.algorithms.algorithm import Algorithm, AlgorithmDefinition

from specparam.tests.tdata import default_spectrum_params

from specparam.algorithms.spectral_fit import *

###################################################################################################
###################################################################################################

def test_algorithm_inherit(tfm):

    class TestAlgo(BaseModel):
        def __init__(self):
            BaseModel.__init__(self, aperiodic_mode='fixed',
                               periodic_mode='gaussian', verbose=False)
            self.data = BaseData()
            self.add_data = self.data.add_data
            self.results = BaseResults(modes=self.modes)
            self.algorithm = SpectralFitAlgorithm(\
                data=self.data, results=self.results, modes=self.modes)
            self.fit = tfm.fit

    talgo = TestAlgo()
    assert isinstance(talgo.algorithm, Algorithm)
    assert isinstance(talgo.algorithm.definition, AlgorithmDefinition)
    talgo.fit(*sim_power_spectrum(*default_spectrum_params()))
