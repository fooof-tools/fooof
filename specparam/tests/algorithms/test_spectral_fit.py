"""Tests for specparam.algorthms.spectral_fit."""

from specparam.models.base import BaseModel
from specparam.data.data import Data
from specparam.results.results import Results
from specparam.sim import sim_power_spectrum
from specparam.algorithms.algorithm import Algorithm

from specparam.tests.tdata import default_spectrum_params

from specparam.algorithms.spectral_fit import *

###################################################################################################
###################################################################################################

def test_algorithm_inherit(tfm):

    class TestAlgo(BaseModel):
        def __init__(self):
            BaseModel.__init__(self, aperiodic_mode='fixed', periodic_mode='gaussian',
                               converters=None, verbose=False)
            self.data = Data()
            self.add_data = self.data.add_data
            self.results = Results(modes=self.modes)
            self.algorithm = SpectralFitAlgorithm(\
                data=self.data, results=self.results, modes=self.modes)
            self.fit = tfm.fit

    talgo = TestAlgo()
    assert isinstance(talgo.algorithm, Algorithm)
    talgo.fit(*sim_power_spectrum(*default_spectrum_params()))
