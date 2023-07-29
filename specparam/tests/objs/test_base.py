"""Tests for specparam.objs.base, including the base object and it's methods."""

from specparam.sim import sim_power_spectrum

# TEMP:
from specparam.objs.bfit import BaseFit
from specparam.objs.data import BaseData

from specparam.objs.base import *

###################################################################################################
###################################################################################################

# def test_base_object():
#     """Check base object initializes properly."""

#     assert BaseSpectralModel()

def test_base_fit():

    class TestBase(BaseSpectralModel, BaseFit, BaseData):
        def __init__(self):
            BaseData.__init__(self)
            BaseFit.__init__(self, aperiodic_mode='fixed', periodic_mode='gaussian')
            BaseSpectralModel.__init__(self)

    tbase = TestBase()
    tbase.fit(*sim_power_spectrum([3, 50], [50, 2], [10, 0.5, 2, 20, 0.3, 4]))
