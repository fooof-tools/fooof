"""Test functions for fooof.utils.params."""

import numpy as np

from fooof.utils.params import *

###################################################################################################
###################################################################################################

def test_compute_knee_frequency():

    assert compute_knee_frequency(100, 2)

def test_compute_time_constant():

    assert compute_time_constant(100)
