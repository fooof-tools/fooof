"""Test functions for fooof.analysis.error."""

from fooof.analysis.error import *

###################################################################################################
###################################################################################################

def test_compute_pointwise_error_fm(tfm):

    compute_pointwise_error_fm(tfm, True, True)

def test_compute_pointwise_error_fg(tfg):

    compute_pointwise_error_fg(tfg, True, True)
