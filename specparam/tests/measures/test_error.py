"""Test functions for specparam.measures.error."""

from specparam.measures.error import *

###################################################################################################
###################################################################################################

def test_compute_pointwise_error(tfm):

    errs = compute_pointwise_error(tfm, False, True)
    assert np.all(errs)

def test_compute_pointwise_error_plt(tfm, skip_if_no_mpl):
    """Run a separate test to run with plot pass-through."""

    compute_pointwise_error(tfm, True, False)

def test_compute_pointwise_error_group(tfg):

    errs = compute_pointwise_error_group(tfg, False, True)
    assert np.all(errs)

def test_compute_pointwise_error_group_plt(tfg, skip_if_no_mpl):
    """Run a separate test to run with plot pass-through."""

    compute_pointwise_error_group(tfg, True, False)

def test_compute_pointwise_error_arr():

    d1 = np.ones(5) * 2
    d2 = np.ones(5)

    errs = compute_pointwise_error_arr(d1, d2)
    assert np.array_equal(errs, np.array([1, 1, 1, 1, 1]))
