"""Test functions for fooof.sim.transform"""

import numpy as np

from fooof.sim.gen import gen_power_spectrum
from fooof.sim.params import SimParams

from fooof.sim.transform import *

###################################################################################################
###################################################################################################

def test_rotate_spectrum():

    # Create a spectrum to use for test rotations
    freqs, spectrum = gen_power_spectrum([1, 100], [1, 1], [])

    # Check that rotation transforms the power spectrum
    rotated_spectrum = rotate_spectrum(freqs, spectrum, delta_exponent=0.5, f_rotation=25.)
    assert not np.all(rotated_spectrum == spectrum)

    # Check that 0 rotation returns the same spectrum
    rotated_spectrum = rotate_spectrum(freqs, spectrum, delta_exponent=0., f_rotation=25.)
    assert np.all(rotated_spectrum == spectrum)

def test_translate_spectrum():

    # Create a spectrum to use for test translation
    freqs, spectrum = gen_power_spectrum([1, 100], [1, 1], [])

    # Check that translation transforms the power spectrum
    translated_spectrum = translate_spectrum(spectrum, delta_offset=1.)
    assert not np.all(translated_spectrum == spectrum)

    # Check that 0 translation returns the same spectrum
    translated_spectrum = translate_spectrum(spectrum, delta_offset=0.)
    assert np.all(translated_spectrum == spectrum)

def test_rotate_sim_spectrum():

    sim_params = SimParams([1, 1], [10, 0.5, 1], 0)
    freqs, spectrum = gen_power_spectrum([3, 40], *sim_params)

    rotated_spectrum, new_sim_params = rotate_sim_spectrum(freqs, spectrum, 0.5, 20, sim_params)

    assert not np.all(rotated_spectrum == spectrum)
    assert new_sim_params.aperiodic_params[1] == 1.5

def test_translate_sim_spectrum():

    sim_params = SimParams([1, 1], [10, 0.5, 1], 0)
    freqs, spectrum = gen_power_spectrum([3, 40], *sim_params)

    translated_spectrum, new_sim_params = translate_sim_spectrum(spectrum, 0.5, sim_params)
    assert not np.all(translated_spectrum == spectrum)
    assert new_sim_params.aperiodic_params[0] == 1.5

def test_compute_rotation_offset():

    assert compute_rotation_offset(20, 0.5)

def test_compute_rotation_frequency():

    delta_exp_b, delta_exp_c = 0.5, 0.75
    f_rot_b, f_rot_c = 5, 10

    f_rot_bc = compute_rotation_frequency(delta_exp_b, f_rot_b, delta_exp_c, f_rot_c)

    assert isinstance(f_rot_bc, float)
    assert np.isclose(f_rot_bc, 40.)
