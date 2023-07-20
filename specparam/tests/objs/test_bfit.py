"""Tests for specparam.objs.bfit, including the data object and it's methods."""

from specparam.objs.bfit import *

###################################################################################################
###################################################################################################

def test_base_fit_object():
    """Check base object initializes properly."""

    assert BaseFit(aperiodic_mode='fixed', periodic_mode='gaussian')
