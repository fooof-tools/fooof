"""Tests for the FOOOFGroup fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
	They serve rather as 'smoke tests', for if anything fails completely.
"""

import os
import pkg_resources as pkg

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

	fg.fit(xs, ys)

	out = fg.get_group_results()

	assert out

def test_fooof_group_fit_save_load():
	"""Check that FOOOFGroup saves and loads."""

	xs, ys = mk_fake_group_data(np.arange(3, 50, 0.5))

	file_name = 'test_fooof_group'
	file_path = pkg.resource_filename(__name__, 'test_files')

	fg = FOOOFGroup()

	fg.fit(xs, ys, save_dat=True, file_name=file_name, file_path=file_path)

	assert os.path.exists(os.path.join(file_path, file_name + '.json'))

	nfg = FOOOFGroup()
	nfg.load(file_name=file_name, file_path=file_path)

	out = nfg.get_group_results()

	assert out

def test_fooof_group_plot_get_report():
	"""Check methods that print, plot, and create report."""

	xs, ys = mk_fake_group_data(np.arange(3, 50, 0.5))

	fg = FOOOFGroup()

	fg.fit(xs, ys)

	fg.print_results()

	fg.plot()

	file_name = 'test_group_report'
	file_path = pkg.resource_filename(__name__, 'test_reports')

	fg.create_report(save_name=file_name, save_path=file_path)

	assert os.path.exists(os.path.join(file_path, file_name + '.pdf'))
