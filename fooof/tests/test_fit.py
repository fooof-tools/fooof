"""Tests for the FOOOF fit object and methods.

NOTES
-----
The tests here are not strong tests for accuracy.
	They serve rather as 'smoke tests', for if anything fails completely.
"""

from py.test import raises

import os
import numpy as np
import pkg_resources as pkg

from fooof import FOOOF
from fooof.tests.utils import mk_fake_data

##########################################################################################
##########################################################################################

def test_fooof():
	"""Check FOOOF object initializes properly."""

	assert FOOOF()

def test_fooof_fit_nk():
	"""Test FOOOF fit, no knee."""

	xs = np.arange(3, 50, 0.5)
	bgp = [50, 2]
	oscs = [[10, 0.5, 2],
			[20, 0.3, 4]]

	xs, ys = mk_fake_data(xs, bgp, [it for osc in oscs for it in osc])

	fm = FOOOF()
	fm.fit(xs, ys)

	# Check model results - background parameters
	assert np.all(np.isclose(bgp, fm.background_params_, [0.5, 0.1]))

	# Check model results - gaussian parameters
	for i, osc in enumerate(oscs):
		assert np.all(np.isclose(osc, fm._gaussian_params[i], [1, 0.2, 0.5]))

def test_fooof_checks():
	"""Test various checks, errors and edge cases in FOOOF."""

	xs, ys = mk_fake_data(np.arange(3, 50, 0.5), [50, 2], [10, 0.5, 2])

	fm = FOOOF()

	# Check dimension error
	with raises(ValueError):
		fm.fit(xs, np.reshape(ys, [1, len(ys)]))

	# Check shape mismatch error
	with raises(ValueError):
		fm.fit(xs[:-1], ys)

	# Check trim_psd range
	fm.fit(xs, ys, [3, 40])

	# Check freq of 0 issue
	xs, ys = mk_fake_data(np.arange(0, 50, 0.5), [50, 2], [10, 0.5, 2])
	fm.fit(xs, ys)

	# Check fit, plot and string report model error (no data / model fit)
	fm = FOOOF()
	with raises(ValueError):
		fm.fit()
	with raises(ValueError):
		fm.print_results()
	with raises(ValueError):
		fm.plot()

def test_fooof_prints_plot_get_report():
	"""Test methods that print, plot, return run through.

	Checks: print_settings, print_results, plot, get_results, create_report

	Note: minimal test - that methods run. No accuracy checking.
	"""

	xs, ys = mk_fake_data(np.arange(3, 50, 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4])

	fm = FOOOF()

	fm.print_settings()

	fm.fit(xs, ys)

	fm.print_results()

	fm.plot()

	out = fm.get_results()
	assert out

	file_name = 'test_report'
	file_path = pkg.resource_filename(__name__, 'test_reports')

	fm.create_report(save_name=file_name, save_path=file_path)

	assert os.path.exists(os.path.join(file_path, file_name + '.pdf'))

def test_fooof_save_load_str():
	"""Check that FOOOF object saves & loads - given str input."""

	xs, ys = mk_fake_data(np.arange(3, 50, 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4])

	fm = FOOOF()
	fm.fit(xs, ys)

	file_name = 'test_fooof'
	file_path = pkg.resource_filename(__name__, 'test_files')

	fm.save(file_name, file_path, True, True, True)

	assert os.path.exists(os.path.join(file_path, file_name + '.json'))

	nfm = FOOOF()
	nfm.load(file_name, file_path)

	assert nfm

def test_fooof_save_load_file_obj():
	"""Check that FOOOF object saves & loads - given file obj input."""

	xs, ys = mk_fake_data(np.arange(3, 50, 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4])

	fm = FOOOF()
	fm.fit(xs, ys)

	file_name = 'test_fooof_obj'
	file_path = pkg.resource_filename(__name__, 'test_files')

	# Save, using file-object
	with open(os.path.join(file_path, file_name + '.json'), 'w') as save_file_obj:
		fm.save(save_file_obj, file_path, True, False, False)
		fm.save(save_file_obj, file_path, False, True, False)
		fm.save(save_file_obj, file_path, False, False, True)

	assert os.path.exists(os.path.join(file_path, file_name + '.json'))

	nfm1, nfm2, nfm3 = FOOOF(), FOOOF(), FOOOF()

	# Load, using file object
	with open(os.path.join(file_path, file_name + '.json'), 'r') as load_file_obj:
		nfm1.load(load_file_obj, file_path)
		nfm2.load(load_file_obj, file_path)
		nfm3.load(load_file_obj, file_path)

	assert nfm1 and nfm2 and nfm3

def test_fooof_reset_dat():
	"""Check that all relevant data is cleared in the resest method."""

	fm = FOOOF()

	fm.model(*mk_fake_data(np.arange(3, 50, 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4]))
	fm._reset_dat()

	assert fm.freqs is None and fm.psd is None and fm.freq_range is None \
		and fm.freq_res is None and fm.psd_fit_ is None and fm.background_params_ is None \
		and fm.oscillation_params_ is None and fm.r2_ is None and fm.error_ is None \
		and fm._psd_flat is None and fm._psd_osc_rm is None and fm._gaussian_params is None \
		and fm._background_fit is None and fm._oscillation_fit is None
