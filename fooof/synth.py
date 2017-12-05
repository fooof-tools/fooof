"""Creating synthetic PSDs for using with, and testing, FOOOF."""

import numpy as np

from fooof.funcs import gaussian_function, expo_function, expo_nk_function

##########################################################################################
##########################################################################################

def mk_fake_data(xs, bgp, oscs, knee=False, nlv=0.005):
	"""Create fake PSD for testing.

	Parameters
	----------
	xs : 1d array
		Frequency vector to create fake PSD with.
	bgp : list of [float, float, float]
		Parameters to create the background of PSD.
	oscs : list of [float, float, float]
		Parameters to create oscillations. Length of n_oscs * 3.
	knee : bool, optional
		Whether to generate PSD with a knee of not. Default: False
	nlv : float, optional
		Noise level to add to generated PSD. Default: 0.005

	Returns
	-------
	xs : 1d array
		Frequency values (linear).
	ys : 1d array
		Power values (linear).
	"""

	bg = expo_function(xs, *bgp) if knee else expo_nk_function(xs, *bgp)
	oscs = gaussian_function(xs, *oscs)
	noise = np.random.normal(0, nlv, len(xs))

	ys = np.power(10, bg + oscs + noise)

	return xs, ys


def mk_fake_group_data(xs, n_psds=5):
	"""Create a matrix of fake PSDs for testing.

	Parameters
	----------
	xs : 1d array
		Frequency vector to create fake PSDs with.
	n_psds : int, optional
		The number of PSDs to generate in the matrix.

	Returns
	-------
	xs : 1d array
		Frequency values (linear).
	ys : 2d array
		Matrix of power values (linear).
	"""

	ys = np.zeros([n_psds, len(xs)])

	bgp_opts = [[20, 2], [50, 2.5], [35, 1.5]]
	osc_opts = [[], [10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]]

	for i in range(n_psds):
		_, ys[i, :] = mk_fake_data(xs, bgp_opts[np.random.randint(0, len(bgp_opts))],
								   osc_opts[np.random.randint(0, len(osc_opts))])

	return xs, ys
