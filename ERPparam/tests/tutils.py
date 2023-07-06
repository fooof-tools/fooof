"""Utilities for testing fooof."""

from functools import wraps

import numpy as np

from fooof.bands import Bands
from fooof.data import FOOOFResults
from fooof.objs import FOOOF, FOOOFGroup
from fooof.core.modutils import safe_import
from fooof.sim.params import param_sampler
from fooof.sim.gen import gen_power_spectrum, gen_group_power_spectra

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def get_tfm():
    """Get a FOOOF object, with a fit power spectrum, for testing."""

    freq_range = [3, 50]
    ap_params = [50, 2]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = gen_power_spectrum(freq_range, ap_params, gaussian_params)

    tfm = FOOOF(verbose=False)
    tfm.fit(xs, ys)

    return tfm

def get_tfg():
    """Get a FOOOFGroup object, with some fit power spectra, for testing."""

    n_spectra = 3
    xs, ys = gen_group_power_spectra(n_spectra, *default_group_params())

    tfg = FOOOFGroup(verbose=False)
    tfg.fit(xs, ys)

    return tfg

def get_tbands():
    """Get a bands object, for testing."""

    return Bands({'theta' : (4, 8), 'alpha' : (8, 12), 'beta' : (13, 30)})

def get_tresults():
    """Get a FOOOFResults objet, for testing."""

    return FOOOFResults(aperiodic_params=np.array([1.0, 1.00]),
                        peak_params=np.array([[10.0, 1.25, 2.0], [20.0, 1.0, 3.0]]),
                        r_squared=0.97, error=0.01,
                        gaussian_params=np.array([[10.0, 1.25, 1.0], [20.0, 1.0, 1.5]]))

def default_group_params():
    """Create default parameters for generating a test group of power spectra."""

    freq_range = [3, 50]
    ap_opts = param_sampler([[20, 2], [50, 2.5], [35, 1.5]])
    gauss_opts = param_sampler([[10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]])

    return freq_range, ap_opts, gauss_opts

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
