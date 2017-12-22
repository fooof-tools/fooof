"""Utilities for testing fooof."""

from fooof import FOOOF, FOOOFGroup
from fooof.synth import gen_power_spectrum, gen_group_power_spectra

###################################################################################################
###################################################################################################

def get_tfm():
    """Get a FOOOF object, with a fit PSD, for testing."""

    freq_range = [3, 50]
    bg_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum(freq_range, bg_params, gauss_params)

    tfm = FOOOF()
    tfm.fit(xs, ys)

    return tfm

def get_tfg():
    """Get a FOOOFGroup object, with some fit PSDs, for testing."""

    n_psds = 2
    xs, ys = gen_group_power_spectra(n_psds, *default_group_params())

    tfg = FOOOFGroup()
    tfg.fit(xs, ys)

    return tfg

def default_group_params():
    """Create default parameters for generating a test group of power spectra."""

    freq_range = [3, 50]
    bgp_opts = [[20, 2], [50, 2.5], [35, 1.5]]
    gauss_opts = [[], [10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]]

    return freq_range, bgp_opts, gauss_opts
