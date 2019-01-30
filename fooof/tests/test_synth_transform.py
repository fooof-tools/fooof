"""Test functions for FOOOF synth.transform"""

import numpy as np

from fooof.synth.gen import gen_power_spectrum
from fooof.synth.transform import *

###################################################################################################
###################################################################################################

def test_rotate_spectrum():

    # Create a spectrum to use for test rotations
    freqs, spectrum = gen_power_spectrum([1, 100], [1, 1], [])

    # Check that rotation transforms the power spectrum
    rotated_spectrum = rotate_spectrum(freqs, spectrum, delta_f=0.5, f_rotation=25.)
    assert not np.all(rotated_spectrum == spectrum)

    # Check that 0 rotation returns the same spectrum
    rotated_spectrum = rotate_spectrum(freqs, spectrum, delta_f=0., f_rotation=25.)
    assert np.all(rotated_spectrum == spectrum)
