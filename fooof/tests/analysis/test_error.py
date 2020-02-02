"""Test functions for fooof.analysis.error."""

from fooof.analysis.error import *

###################################################################################################
###################################################################################################

def test_compute_pointwise_error_fm(tfm):

    errs = compute_pointwise_error_fm(tfm, False, True)
    assert np.all(errs)

def test_compute_pointwise_error_fm_plt(tfm, skip_if_no_mpl):
    """Run a seperate test to run with plot pass-through."""

    compute_pointwise_error_fm(tfm, True, False)

def test_compute_pointwise_error_fg(tfg):

    errs = compute_pointwise_error_fg(tfg, False, True)
    assert np.all(errs)

def test_compute_pointwise_error_fg_plt(tfm, skip_if_no_mpl):
    """Run a seperate test to run with plot pass-through."""

    compute_pointwise_error_fg(tfm, True, False)
