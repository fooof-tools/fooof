"""Tests for funcs from fooof."""

import numpy as np
from scipy.stats import normaltest

from fooof.funcs import gaussian_function, loglorentzian_function, loglorentzian_nk_function

###################################################################################################
###################################################################################################

def test_gaussian_function():

	xs = np.arange(1, 100)
	ys = gaussian_function(xs, 50, 5, 10)

	assert np.all(ys)

	t, p = normaltest(ys)

	assert p < 0.001

def test_loglorentzian_function():

	xs = np.arange(1, 100)
	ys = loglorentzian_function(xs, 2, 10, 100)

	assert True

def test_loglorentizian_nk_function():

	xs = np.arange(1, 100)
	ys = loglorentzian_function(xs, 2, 100)

	assert True
