"""Utilities for testing spectral parameterization."""

from functools import wraps

import numpy as np

from specparam.bands import Bands
from specparam.data import FitResults
from specparam.objs import SpectralModel, SpectralGroupModel
from specparam.objs.data import BaseData, BaseData2D
from specparam.core.modutils import safe_import
from specparam.sim.params import param_sampler
from specparam.sim.sim import sim_power_spectrum, sim_group_power_spectra

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def get_tdata():

    tdata = BaseData()
    tdata.add_data(*sim_power_spectrum(*default_spectrum_params()))

    return tdata

def get_tdata2d():

    n_spectra = 3
    tdata2d = BaseData2D()
    tdata2d.add_data(*sim_group_power_spectra(n_spectra, *default_group_params()))

    return tdata2d

def get_tfm():
    """Get a model object, with a fit power spectrum, for testing."""

    tfm = SpectralModel(verbose=False)
    tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

    return tfm

def get_tfg():
    """Get a group object, with some fit power spectra, for testing."""

    n_spectra = 3
    tfg = SpectralGroupModel(verbose=False)
    tfg.fit(*sim_group_power_spectra(n_spectra, *default_group_params()))

    return tfg

def get_tbands():
    """Get a bands object, for testing."""

    return Bands({'theta' : (4, 8), 'alpha' : (8, 12), 'beta' : (13, 30)})

def get_tresults():
    """Get a FitResults object, for testing."""

    return FitResults(aperiodic_params=np.array([1.0, 1.00]),
                      peak_params=np.array([[10.0, 1.25, 2.0], [20.0, 1.0, 3.0]]),
                      r_squared=0.97, error=0.01,
                      gaussian_params=np.array([[10.0, 1.25, 1.0], [20.0, 1.0, 1.5]]))

def get_tdocstring():
    """Get an example docstring, for testing."""

    docstring = \
    """This is a test doctring.

    Parameters
    ----------
    first : thing
        Words, words, words.
    second : stuff
        Words, words, words.

    Returns
    -------
    out : yay
        Words, words, words.
    """

    return docstring

def default_spectrum_params():

    freq_range = [3, 50]
    ap_params = [1, 1]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    return freq_range, ap_params, gaussian_params

def default_group_params():
    """Create default parameters for simulating a test group of power spectra."""

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
