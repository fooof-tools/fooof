"""Utilities for testing fooof."""

from functools import wraps

from fooof import FOOOF, FOOOFGroup
from fooof.synth import gen_power_spectrum, gen_group_power_spectra, param_sampler
from fooof.core.modutils import safe_import

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def get_tfm():
    """Get a FOOOF object, with a fit power spectrum, for testing."""

    freq_range = [3, 50]
    bg_params = [50, 2]
    gauss_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum(freq_range, bg_params, gauss_params)

    tfm = FOOOF()
    tfm.fit(xs, ys)

    return tfm

def get_tfg():
    """Get a FOOOFGroup object, with some fit power spectra, for testing."""

    n_spectra = 2
    xs, ys, _ = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup()
    tfg.fit(xs, ys)

    return tfg

def default_group_params():
    """Create default parameters for generating a test group of power spectra."""

    freq_range = [3, 50]
    bgp_opts = param_sampler([[20, 2], [50, 2.5], [35, 1.5]])
    gauss_opts = param_sampler([[10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]])

    return freq_range, bgp_opts, gauss_opts

def plot_test(func):
    """Decorator for simple testing of plotting functions.

    Notes
    -----
    This decorator closes all plots prior to the test.
    After running the test function, it checks an axis was created with data.
    It therefore performs a minimal test - asserting the plots exists, with no accuracy checking.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):

        plt.close('all')

        func(*args, **kwargs)

        ax = plt.gca()
        assert ax.has_data()

    return wrapper
