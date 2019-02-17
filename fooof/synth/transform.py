"""Functions and utilities for transforming power spectra."""

import numpy as np

from fooof.synth.params import update_syn_ap_params

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
        Change in aperiodic exponent to be applied.
        Positive is clockwise rotation (steepen).
        Negative is counterclockwise rotation (flatten).
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.
    """

    mask = (np.abs(freqs) / f_rotation)**-delta
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


def rotate_syn_spectrum(freqs, power_spectrum, delta, f_rotation, syn_params):
    """Rotate a power spectrum about a frequency point, changing the power law exponent.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum that is to be rotated.
    delta : float
        Change in aperiodic exponent to be applied.
        Positive is clockwise rotation (steepen).
        Negative is counterclockwise rotation (flatten).
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.
    syn_params : SynParams object
        Object storing the current parameter definitions.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.
    new_syn_params : SynParams object
        Updated object storing the new parameter definitions.
    """

    rotated_spectrum = rotate_spectrum(freqs, power_spectrum, delta, f_rotation)
    delta_offset = calc_rot_offset(delta, f_rotation)

    new_syn_params = update_syn_ap_params(syn_params, [delta_offset, delta])

    return rotated_spectrum, new_syn_params


def translate_syn_spectrum(power_spectrum, delta, syn_params):
    """Translate a spectrum, changing the offset value.

    Parameters
    ----------
    power_spectrum : 1d array
        Power values of the spectrum that is to be translated.
    delta : float
        Amount to change the offset by.
        Positive is an upwards translation.
        Negative is a downwards translation.
    syn_params : SynParams object
        Object storing the current parameter definitions.

    Returns
    -------
    translated_spectrum : 1d array
        Translated power spectrum.
    new_syn_params : SynParams object
        Updated object storing the new parameter definitions.
    """

    translated_spectrum = translate_spectrum(power_spectrum, delta)
    new_syn_params = update_syn_ap_params(syn_params, delta, 'intercept')

    return translated_spectrum, new_syn_params


def calc_rot_offset(delta, f_rotation):
    """Calculate the change in offset from a given rotation.

    Parameters
    ----------
    delta : float
        Change in aperiodic exponent to be applied.
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.

    Returns
    -------
    float
        The amount the offset will change for the specified exponent change.
    """

    return -np.log10(f_rotation) * -delta
