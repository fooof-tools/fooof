"""Functions and utilities for transforming power spectra."""

import numpy as np

###################################################################################################
###################################################################################################

def rotate_spectrum(freqs, power_spectrum, delta, f_rotation):
    """Rotate a power spectrum about a frequency point, changing the power law exponent.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum that is to be rotated.
    delta : float
        Change in power law exponent to be applied.
        Positive is counterclockwise rotation (flatten).
        Negative is clockwise rotation (steepen).
    f_rotation : float
        Frequency (Hz) at which to do the rotation, such that power at that frequency is unchanged.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.
    """

    mask = (np.abs(freqs) / f_rotation)**delta
    rotated_spectrum = mask * power_spectrum

    return rotated_spectrum


def translate_spectrum(power_spectrum, delta):
    """Translate a spectrum, changing the offset value.

    Parameters
    ----------
    power_spectrum : 1d array
        Power values of the spectrum that is to be translated.
    delta : float
        Amount to change the offset by.
        Positive is an upwards translation.
        Negative is a downwards translation.

    Returns
    -------
    translated_spectrum : 1d array
        Translated power spectrum.
    """

    translated_spectrum = np.power(10, delta, dtype='float') * power_spectrum

    return translated_spectrum


def calc_rot_offset(delta, f_rotation):
    """Calculate the change in offset from a given rotation"""

    return -np.log10(f_rotation) * delta
