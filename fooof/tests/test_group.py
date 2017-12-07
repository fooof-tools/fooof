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
from fooof.synth import mk_fake_group_data
from fooof.utils import mk_freq_vector

##########################################################################################
##########################################################################################

def test_fooof_group():
	"""Check FOOOFGroup object initializes properly."""

	assert FOOOFGroup()

def test_fooof_group_fit():
	"""Test FOOOFGroup fit, no knee."""

	xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5))

	fg = FOOOFGroup()

	fg.fit(xs, ys)

	out = fg.get_results()

	assert out

def test_fooof_group_fit_par():
	"""Test FOOOFGroup fit, running in parallel."""

	xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5))

	fg = FOOOFGroup()

	fg.fit(xs, ys, n_jobs=-1)

	out = fg.get_results()

	assert out

def test_fooof_group_save_load():
	"""Test that FOOOFGroup saves and loads, including settings & results."""

	xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5))

	set_file_name = 'test_fooof_group_set'
	res_file_name = 'test_fooof_group_res'
	file_path = pkg.resource_filename(__name__, 'test_files')

	fg = FOOOFGroup(min_amp=0.01)

	fg.fit(xs, ys)
	fg.save(save_file=set_file_name, save_path=file_path, save_settings=True)
	fg.save(save_file=res_file_name, save_path=file_path, save_results=True)

	assert os.path.exists(os.path.join(file_path, set_file_name + '.json'))
	assert os.path.exists(os.path.join(file_path, res_file_name + '.json'))

	nfg = FOOOFGroup()

	nfg.load(file_name=set_file_name, file_path=file_path)
	assert nfg.min_amp == 0.01

	nfg.load(file_name=res_file_name, file_path=file_path)
	assert nfg.get_results()

def test_fooof_group_plot_get_report():
	"""Check methods that print, plot, and create report."""

	xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5))

	fg = FOOOFGroup()

	fg.fit(xs, ys)

	fg.print_results()

	fg.plot()

	file_name = 'test_group_report'
	file_path = pkg.resource_filename(__name__, 'test_reports')

	fg.create_report(save_name=file_name, save_path=file_path)

	assert os.path.exists(os.path.join(file_path, file_name + '.pdf'))

def test_fooof_group_model():
	"""Check that running the top level model method runs."""

	xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5))

	fg = FOOOFGroup()

	fg.model(xs, ys)

	assert fg
