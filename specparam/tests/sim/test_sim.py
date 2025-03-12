"""Test functions for specparam.sim.sim"""

import numpy as np
from numpy import array_equal

from specparam.tests.tdata import default_group_params

from specparam.sim.sim import *

###################################################################################################
###################################################################################################

def test_sim_power_spectrum():

    freq_range = [3, 50]
    ap_params = [50, 2]
    pe_params = [10, 0.5, 2, 20, 0.3, 4]

    xs, ys = sim_power_spectrum(freq_range, ap_params, pe_params)

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

    # Test with a rotation applied returned
    f_rotation = 20
    xs, ys = sim_power_spectrum(freq_range, ap_params, pe_params, f_rotation=f_rotation)

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

def test_sim_power_spectrum_return_params():

    freq_range = [3, 50]
    ap_params = [50, 2]
    pe_params = [[10, 0.5, 2], [20, 0.3, 4]]
    nlv = 0.01

    xs, ys, sp = sim_power_spectrum(freq_range, ap_params, pe_params,
                                    nlv, return_params=True)

    # Test returning parameters
    assert array_equal(sp.aperiodic_params, ap_params)
    assert array_equal(sp.periodic_params, pe_params)
    assert sp.nlv == nlv

def test_sim_group_power_spectra():

    n_spectra = 3

    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params())

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == 2
    assert ys.shape[0] == n_spectra

    # Test the case in which periodic params are an empty list
    xs, ys = sim_group_power_spectra(2, [3, 50], [1, 1], [])

    assert np.all(xs)
    assert np.all(ys)

    # Test with a rotation applied returned
    f_rotation = 20
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params(), f_rotation=f_rotation)

    assert np.all(xs)
    assert np.all(ys)

def test_sim_group_power_spectra_return_params():

    n_spectra = 3

    aps = [1, 1]
    pes = [10, 0.5, 1]
    nlv = 0.01

    xs, ys, sim_params = sim_group_power_spectra(n_spectra, [1, 50], aps, pes, nlv,
                                                 return_params=True)

    assert n_spectra == ys.shape[0] == len(sim_params)
    sp = sim_params[0]
    assert array_equal(sp.aperiodic_params, aps)
    assert array_equal(sp.periodic_params, [pes])
    assert sp.nlv == nlv

def test_sim_spectrogram():

    n_windows = 3

    xs, ys = sim_spectrogram(n_windows, *default_group_params())

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == 2
    assert ys.shape[1] == n_windows
