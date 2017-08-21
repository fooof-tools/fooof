"""Tests for funcs from fooof."""

import numpy as np
from scipy.stats.mstats import normaltest

from fooof.funcs import gaussian_function, linear_function, quadratic_function

##
##

def test_gaussian_function():

	xs = np.arange(1, 100)
	ys = gaussian_function(xs, 50, 5, 10)

	assert np.all(ys)

	t, p = normaltest(ys)

	assert p < 0.001

def test_linear_function():

	xs = np.arange(1, 100)
	ys = linear_function(xs, 1, 1)

	assert np.all(ys)

def test_quadratic_function():

	xs = np.arange(1, 100)
	ys = quadratic_function(xs, 1, 2, 3)

	assert np.all(ys)
