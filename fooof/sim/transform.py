"""Functions and utilities for transforming power spectra."""

import numpy as np

from fooof.sim.params import update_sim_ap_params

###################################################################################################
###################################################################################################

def rotate_spectrum(freqs, power_spectrum, delta_exponent, f_rotation):
    """Rotate a power spectrum about a frequency point, changing the power law exponent.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum that is to be rotated.
    delta_exponent : float
        Change in aperiodic exponent to be applied.
        Positive is clockwise rotation (steepen).
        Negative is counterclockwise rotation (flatten).
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.

    Notes
    -----
    Warning: This function should only be applied to spectra without a knee.
    If using simulated data, this is spectra created in 'fixed' mode.
    This is because the rotation applied will is inconsistent with
    the formulation of knee spectra, and will change them in an
    unspecified way, not just limited to doing the rotation.
    """

    mask = (np.abs(freqs) / f_rotation)**-delta_exponent
    rotated_spectrum = mask * power_spectrum

    return rotated_spectrum


def translate_spectrum(power_spectrum, delta_offset):
    """Translate a spectrum, changing the offset value.

    Parameters
    ----------
    power_spectrum : 1d array
        Power values of the spectrum that is to be translated.
    delta_offset : float
        Amount to change the offset by.
        Positive is an upwards translation.
        Negative is a downwards translation.

    Returns
    -------
    translated_spectrum : 1d array
        Translated power spectrum.
    """

    translated_spectrum = np.power(10, delta_offset, dtype='float') * power_spectrum

    return translated_spectrum


def rotate_sim_spectrum(freqs, power_spectrum, delta_exponent, f_rotation, sim_params):
    """Rotate a simulated power spectrum, updating that SimParams object.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum that is to be rotated.
    delta_exponent : float
        Change in aperiodic exponent to be applied.
        Positive is clockwise rotation (steepen).
        Negative is counterclockwise rotation (flatten).
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.
    sim_params : SimParams object
        Object storing the current parameter definitions.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.
    new_sim_params : SimParams object
        Updated object storing the new parameter definitions.

    Notes
    -----
    Warning: This function should only be applied to spectra without a knee.
    If using simulated data, this is spectra created in 'fixed' mode.
    This is because the rotation applied will is inconsistent with
    the formulation of knee spectra, and will change them in an
    unspecified way, not just limited to doing the rotation.
    """

    rotated_spectrum = rotate_spectrum(freqs, power_spectrum, delta_exponent, f_rotation)
    delta_offset = compute_rotation_offset(delta_exponent, f_rotation)

    new_sim_params = update_sim_ap_params(sim_params, [delta_offset, delta_exponent])

    return rotated_spectrum, new_sim_params


def translate_sim_spectrum(power_spectrum, delta_offset, sim_params):
    """Translate a simulated spectrum, updating that SimParams object.

    Parameters
    ----------
    power_spectrum : 1d array
        Power values of the spectrum that is to be translated.
    delta_offset : float
        Amount to change the offset by.
        Positive is an upwards translation.
        Negative is a downwards translation.
    sim_params : SimParams object
        Object storing the current parameter definitions.

    Returns
    -------
    translated_spectrum : 1d array
        Translated power spectrum.
    new_sim_params : SimParams object
        Updated object storing the new parameter definitions.
    """

    translated_spectrum = translate_spectrum(power_spectrum, delta_offset)
    new_sim_params = update_sim_ap_params(sim_params, delta_offset, 'offset')

    return translated_spectrum, new_sim_params


def compute_rotation_offset(delta_exponent, f_rotation):
    """Calculate the change in offset from a given rotation.

    Parameters
    ----------
    delta_exponent : float
        Change in aperiodic exponent to be applied.
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.

    Returns
    -------
    float
        The amount the offset will change for the specified exponent change.
    """

    return -np.log10(f_rotation) * -delta_exponent
