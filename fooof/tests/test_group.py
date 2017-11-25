"""Tests for the FOOOFGroup fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
	They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np

from fooof import FOOOFGroup
from fooof.tests.utils import mk_fake_group_data

##########################################################################################
##########################################################################################

def test_fooof_group():
	"""Check FOOOFGroup object initializes properly."""

	assert FOOOFGroup()

def test_fooof_group_fit():
	"""Test FOOOFGroup fit, no knee."""

	xs, ys = mk_fake_group_data(np.arange(3, 50, 0.5))

	fg = FOOOFGroup()

	fg.fit_group(xs, ys)

	out = fg.get_group_results()

	assert out