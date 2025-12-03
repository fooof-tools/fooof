"""Data for tests."""

import numpy as np

from specparam.bands import Bands
from specparam.modes.modes import Modes
from specparam.data.data import Data, Data2D, Data2DT, Data3D
from specparam.data.stores import FitResults
from specparam.models import (SpectralModel, SpectralGroupModel,
                              SpectralTimeModel, SpectralTimeEventModel)
from specparam.sim.params import param_sampler
from specparam.sim.sim import sim_power_spectrum, sim_group_power_spectra, sim_spectrogram

###################################################################################################
###################################################################################################

## PARAMETER DEFINITIONS

def default_spectrum_params():

    freq_range = [3, 50]
    ap_params = [1, 1]
    gaussian_params = [10, 0.5, 2, 20, 0.3, 4]

    return freq_range, {'fixed' : ap_params}, {'gaussian' : gaussian_params}

def default_group_params():
    """Create default parameters for simulating a test group of power spectra."""

    freq_range = [3, 50]
    ap_opts = param_sampler([[20, 2], [50, 2.5], [35, 1.5]])
    gauss_opts = param_sampler([[10, 0.5, 2], [10, 0.5, 2, 20, 0.3, 4]])

    return freq_range, {'fixed' : ap_opts}, {'gaussian' : gauss_opts}

## TEST DATA OBJECTS

def get_tdata():

    tdata = Data()
    tdata.add_data(*sim_power_spectrum(*default_spectrum_params()))

    return tdata

def get_tdata2d():

    n_spectra = 3
    tdata2d = Data2D()
    tdata2d.add_data(*sim_group_power_spectra(n_spectra, *default_group_params()))

    return tdata2d

def get_tdata2dt():

    n_spectra = 3
    tdata2dt = Data2DT()
    tdata2dt.add_data(*sim_spectrogram(n_spectra, *default_group_params()))

    return tdata2dt

def get_tdata3d():

    n_events = 2
    n_spectra = 3
    tdata3d = Data3D()
    freqs, spectrogram = sim_spectrogram(n_spectra, *default_group_params())
    tdata3d.add_data(freqs, [spectrogram] * n_events)

    return tdata3d

## TEST MODEL OBJECTS

def get_tfm():
    """Get a model object, with a fit power spectrum, for testing."""

    tfm = SpectralModel(bands=Bands({'alpha' : (7, 14)}),
                        min_peak_height=0.05, peak_width_limits=[1, 8])
    tfm.fit(*sim_power_spectrum(*default_spectrum_params()))

    return tfm

def get_tfm2():
    """Get a model object, with a fit power spectrum, for testing - custom metrics & modes."""

    tfm2 = SpectralModel(bands=Bands({'alpha' : (7, 14), 'beta' : [15, 30]}),
                         min_peak_height=0.05, peak_width_limits=[1, 8],
                         metrics=['error_mse', 'gof_adjrsquared'],
                         aperiodic_mode='knee', periodic_mode='gaussian')
    tfm2.fit(*sim_power_spectrum(*default_spectrum_params()))

    return tfm2

def get_tfg():
    """Get a group object, with some fit power spectra, for testing."""

    n_spectra = 3
    tfg = SpectralGroupModel(bands=Bands({'alpha' : (7, 14)}),
                             min_peak_height=0.05, peak_width_limits=[1, 8])
    tfg.fit(*sim_group_power_spectra(n_spectra, *default_group_params()))

    return tfg

def get_tfg2():
    """Get a group object, with some fit power spectra, for testing - custom metrics & modes."""

    n_spectra = 3
    tfg2 = SpectralGroupModel(bands=Bands({'alpha' : (7, 14), 'beta' : [15, 30]}),
                              min_peak_height=0.05, peak_width_limits=[1, 8],
                              metrics=['error_mse', 'gof_adjrsquared'],
                              aperiodic_mode='knee', periodic_mode='gaussian')
    tfg2.fit(*sim_group_power_spectra(n_spectra, *default_group_params()))

    return tfg2

def get_tft():
    """Get a time object, with some fit power spectra, for testing."""

    n_spectra = 3
    xs, ys = sim_spectrogram(n_spectra, *default_group_params())

    tft = SpectralTimeModel(bands=Bands({'alpha' : (7, 14)}), \
                            min_peak_height=0.05, peak_width_limits=[1, 8],)
    tft.fit(xs, ys)

    return tft

def get_tfe():
    """Get an event object, with some fit power spectra, for testing."""

    n_spectra = 3
    xs, ys = sim_spectrogram(n_spectra, *default_group_params())
    ys = [ys, ys]

    tfe = SpectralTimeEventModel(bands=Bands({'alpha' : (7, 14)}),
                                 min_peak_height=0.05, peak_width_limits=[1, 8],)
    tfe.fit(xs, ys)

    return tfe

## TEST OTHER OBJECTS

def get_tbands():
    """Get a bands object, for testing."""

    return Bands({'theta' : (4, 8), 'alpha' : (8, 12), 'beta' : (13, 30)})

def get_tmodes():
    """Get a Modes object, for testing."""

    return Modes(aperiodic='fixed', periodic='gaussian')

def get_tresults():
    """Get a FitResults object, for testing."""

    return FitResults(aperiodic_fit=np.array([1.0, 1.00]),
                      aperiodic_converted=np.array([np.nan, np.nan]),
                      peak_fit=np.array([[10.0, 1.25, 1.0], [20.0, 1.0, 1.5]]),
                      peak_converted=np.array([[10.0, 1.25, 2.0], [20.0, 1.0, 3.0]]),
                      metrics={'error_mae' : 0.01, 'gof_rsquared' : 0.97})

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
