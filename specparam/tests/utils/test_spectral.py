"""Test functions for specparam.utils.spectral."""

import numpy as np

from specparam.sim import sim_power_spectrum, sim_group_power_spectra

from specparam.utils.spectral import *

###################################################################################################
###################################################################################################

def test_trim_spectrum():

    f_in = np.array([0., 1., 2., 3., 4., 5.])
    p_in = np.array([1., 2., 3., 4., 5., 6.])

    f_out, p_out = trim_spectrum(f_in, p_in, [2., 4.])

    assert np.array_equal(f_out, np.array([2., 3., 4.]))
    assert np.array_equal(p_out, np.array([3., 4., 5.]))

def test_interpolate_spectrum():

    # Test with single buffer exclusion zone
    freqs, powers = sim_power_spectrum(\
        [1, 75], {'fixed' : [1, 1]}, {'gaussian' : [[10, 0.5, 1.0], [60, 2, 0.1]]})

    exclude = [58, 62]

    freqs_out, powers_out = interpolate_spectrum(freqs, powers, exclude)

    assert np.array_equal(freqs, freqs_out)
    assert np.all(powers)
    assert powers.shape == powers_out.shape
    mask = np.logical_and(freqs >= exclude[0], freqs <= exclude[1])
    assert powers[mask].sum() > powers_out[mask].sum()

    # Test with multiple buffer exclusion zones
    freqs, powers = sim_power_spectrum([1, 150], \
        {'knee' : [1, 100, 1]}, {'gaussian' : [[10, 0.5, 1.0], [60, 1, 0.1], [120, 0.5, 0.1]]})

    exclude = [[58, 62], [118, 122]]

    freqs_out, powers_out = interpolate_spectrum(freqs, powers, exclude)
    assert np.array_equal(freqs, freqs_out)
    assert np.all(powers)
    assert powers.shape == powers_out.shape

    for f_range in exclude:
        mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])
        assert powers[mask].sum() > powers_out[mask].sum()

def test_interpolate_spectra():

    freqs, powers = sim_group_power_spectra(\
        5, [1, 150], {'knee' : [1, 100, 1]},
        {'gaussian' : [[10, 0.5, 1.0], [60, 1, 0.1], [120, 0.5, 0.1]]})

    exclude = [[58, 62], [118, 122]]
    freqs_out, powers_out = interpolate_spectra(freqs, powers, exclude)
    assert np.array_equal(freqs, freqs_out)
    assert np.all(powers)
    assert powers.shape == powers_out.shape

    for f_range in exclude:
        mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])
        assert powers[:, mask].sum() > powers_out[:, mask].sum()

def test_subsample_spectra():

    # Simulate spectra, each with unique osc peak (for checking)
    n_sim = 10
    oscs = [[10 + ind, 0.25, 0.5] for ind in range(n_sim)]
    freqs, powers = sim_group_power_spectra(n_sim, [1, 50], {'fixed' : [1, 1]}, {'gaussian' : oscs})

    # Test with int input
    n_select = 2
    out = subsample_spectra(powers, n_select)
    assert isinstance(out, np.ndarray)
    assert out.shape == (n_select, powers.shape[1])

    # Test with foat input
    prop_select = 0.75
    out = subsample_spectra(powers, prop_select)
    assert isinstance(out, np.ndarray)
    assert out.shape == (int(prop_select * n_sim), powers.shape[1])

    # Test returning indices
    out, inds = subsample_spectra(powers, n_select, return_inds=True)
    assert len(set(inds)) == n_select
    for ind, spectrum in zip(inds, out):
        assert np.array_equal(spectrum, powers[ind, :])

    out, inds = subsample_spectra(powers, prop_select, return_inds=True)
    assert len(set(inds)) == int(prop_select * n_sim)
    for ind, spectrum in zip(inds, out):
        assert np.array_equal(spectrum, powers[ind, :])
