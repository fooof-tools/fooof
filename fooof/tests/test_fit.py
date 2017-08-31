"""Tests for the FOOOF module."""

import numpy as np

from fooof import FOOOF
from fooof.funcs import gaussian_function, quadratic_function

##########################################################################################
##########################################################################################

def mk_fake_data(xs, bgp, oscs):
	"""Create fake PSD for testing.

	Parameters
	----------
	xs : 1d array
		Frequency vector to create fake PSD with.
	bgp : list of [float, float, float]
		Parameters to create the background of PSD.
	oscs : list of [float, float, float]
		Parameters to create oscillations. Length of n_oscs * 3.

	Returns
	-------
	xs : 1d array
		Frequency values (linear).
	ys : 1d array
		Power values (linear).
	"""

	bg = quadratic_function(np.log10(xs), *bgp)
	oscs = gaussian_function(xs, *oscs)
	noise = np.random.normal(0, 0.005, len(xs))

	ys = np.power(10, bg + oscs + noise)

	return xs, ys

def test_FOOOF():
	"""Check FOOOF object initializes properly."""

	assert FOOOF()

def test_model():
	"""Test the model test.
	Note: this is (sort of) an 'integration' test - model runs almost every other method.
	"""

	xs = np.arange(3, 40, 0.5)
	bgp = [-20, -0.8, 3e-15]
	oscs = [[10, 0.5, 2],
			[20, 0.3, 4]]

	xs, ys = mk_fake_data(xs, bgp, [it for osc in oscs for it in osc])

	ff = FOOOF()

	ff.model(xs, ys, [3, 40])

	# Check model results - background parameters
	assert np.all(np.isclose(bgp, ff.background_params, [0.5, 0.1, 1e-16]))

	# Check model results - gaussian parameters
	for i, osc in enumerate(oscs):
		assert np.all(np.isclose(osc, ff._gaussian_params[i], [1, 0.2, 0.5]))

def test_reset_dat():

	ff = FOOOF()

	ff.model(*mk_fake_data(np.arange(3, 40, 0.5), [-20, -0.8, 3e-15], [10, 0.5, 2, 20, 0.3, 4]), [3, 40])
	ff._reset_dat()

	assert ff.freqs is None and ff.psd is None and ff.freq_range is None \
		and ff.freq_res is None and ff.psd_fit is None and ff.background_params is None \
		and ff.oscillation_params is None and ff.error is None \
		and ff._psd_flat is None and ff._psd_osc_rm is None and ff._gaussian_params is None \
		and ff._background_fit is None and ff._oscillation_fit is None

# TODO: what are these?

# def test_fit():
# 	pass

# def test_plot():
# 	pass

# def test_print_params():
# 	pass

# def test_drop_osc_overlap():
# 	pass

# def test_drop_osc_bw():
# 	pass

# def test_drop_osc_cf():
# 	pass

# def test_r_squared():
# 	pass

# def test_fit_oscs():
# 	pass

# def test_clean_backgroud_fit():
# 	pass

# def test_quick_background_fit():
# 	pass
