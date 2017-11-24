"""Tests for the FOOOF fit objects and modules.

NOTES
-----
The tests here are not strong tests for accuracy.
	They serve rather as 'smoke tests', for if anything fails completely.
"""

from py.test import raises

import numpy as np
import pkg_resources as pkg

from fooof import FOOOF, FOOOFGroup
from fooof.tests.utils import mk_fake_data, mk_fake_group_data

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
		fm.fit(xs[:-1], ys)

	# Check shape mismatch error
	with raises(ValueError):
		fm.fit(xs, np.reshape(ys, [1, len(ys)]))

	# Check trim_psd range
	fm.fit(xs, ys, [3, 40])

	# Check freq of 0 issue
	xs, ys = mk_fake_data(np.arange(0, 50, 0.5), [50, 2], [10, 0.5, 2])
	fm.fit(xs, ys)

	# Check plot and string report model error
	fm = FOOOF()
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

	fm.create_report(save_path=pkg.resource_filename(__name__, 'reports'))

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
