"""Functions and utilities for transforming power spectra."""

import numpy as np

###################################################################################################
###################################################################################################

def rotate_spectrum(freqs, power_spectrum, delta_f, f_rotation):
    """Rotate a power spectrum about a frequency point, changing the power law exponent.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum that is to be rotated.
    delta_f : float
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

    # Check that the requested frequency rotation value is within the given range
    if f_rotation < freqs.min() or f_rotation > freqs.max():
        raise ValueError('Rotation frequency not within frequency range.')

    f_mask = np.zeros_like(freqs)

    f_mask = 10**(np.log10(np.abs(freqs)) * (delta_f))

    # If starting freq is 0Hz, default power at 0Hz to keep same value because log will return inf.
    if freqs[0] == 0.:
        f_mask[0] = 1.

    f_mask = f_mask / f_mask[np.where(freqs >= f_rotation)[0][0]]

    rotated_spectrum = f_mask * power_spectrum

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
