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

def test_compute_pointwise_error_fg_plt(tfg, skip_if_no_mpl):
    """Run a seperate test to run with plot pass-through."""

    compute_pointwise_error_fg(tfg, True, False)

def test_compute_pointwise_error():

    d1 = np.ones(5) * 2
    d2 = np.ones(5)

    errs = compute_pointwise_error(d1, d2)
    assert np.array_equal(errs, np.array([1, 1, 1, 1, 1]))
