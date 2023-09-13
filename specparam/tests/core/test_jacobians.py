"""Tests for specparam.core.jacobians."""

from specparam.core.jacobians import *

###################################################################################################
###################################################################################################

def test_jacobian_gauss():

    xs = np.arange(1, 100)
    ctr, hgt, wid = 50, 5, 10

    jacobian = jacobian_gauss(xs, ctr, hgt, wid)
    assert isinstance(jacobian, np.ndarray)
    assert jacobian.shape == (len(xs), 3)

def test_jacobian_expo():

    xs = np.arange(1, 100)
    off, knee, exp = 10, 5, 2

    jacobian = jacobian_expo(xs, off, knee, exp)
    assert isinstance(jacobian, np.ndarray)
    assert jacobian.shape == (len(xs), 3)

def test_jacobian_expo_nk():

    xs = np.arange(1, 100)
    off, exp = 10, 2

    jacobian = jacobian_expo_nk(xs, off, exp)
    assert isinstance(jacobian, np.ndarray)
    assert jacobian.shape == (len(xs), 2)
