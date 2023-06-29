"""Functions and utilities for transforming power spectra."""

import numpy as np

from specparam.sim.params import update_sim_ap_params

###################################################################################################
###################################################################################################

def rotate_spectrum(freqs, power_spectrum, delta_exponent, f_rotation):
    """Rotate a power spectrum about a frequency point, changing the aperiodic exponent.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum.
    delta_exponent : float
        Change in aperiodic exponent to be applied, where:

        - positive is clockwise rotation (steepen)
        - negative is counterclockwise rotation (flatten)
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.

    Raises
    ------
    ValueError
        If the rotation frequency is invalid.

    Notes
    -----
    Rotating in log-log spacing is equivalent to multiplying with a 1/f shaped mask that is:

    - unity at the rotation frequency
    - has an exponent of the desired delta exponent

    This mask, when applied to a spectrum as 'spectrum * mask', should result in:

    - rotated_spectrum = 1/f^(original_exponent + delta_exponent), where
    - spectrum[rotation_frequency] == rotated spectrum[rotation_frequency]

    This mask is defined as:

    - mask = (freqs / rotation_frequency) ** -delta_exponent

    Note that this approach / function should only be applied to spectra without a knee:

    - If using simulated data, this is spectra created in 'fixed' mode.
    - This is because the rotation applied is inconsistent with the formulation of spectra
      with a knee. This transformation will change them in an unspecified way, not just
      limited to doing the rotation.

    Examples
    --------
    Rotate a simulated spectrum, changing the exponent around a rotation point of 25 Hz:

    >>> from specparam.sim import sim_power_spectrum
    >>> freqs, powers = sim_power_spectrum([1, 50], [1, 1], [10, 0.5, 1])
    >>> rotated_powers = rotate_spectrum(freqs, powers, 0.5, 25)
    """

    # Rotations are undefined for frequency value of exactly zero
    #   We also do not support (in this implementation) negative frequencies
    if f_rotation <= 0.:
        raise ValueError("The rotation frequency cannot be less than or equal to zero.")

    mask = (np.abs(freqs) / f_rotation)**-delta_exponent
    rotated_spectrum = mask * power_spectrum

    return rotated_spectrum


def translate_spectrum(power_spectrum, delta_offset):
    """Translate a spectrum, changing the offset value.

    Parameters
    ----------
    power_spectrum : 1d array
        Power values of the spectrum.
    delta_offset : float
        Amount to change the offset by, where:

        - positive values are an upwards translation
        - negative are are a downwards translation

    Returns
    -------
    translated_spectrum : 1d array
        Translated power spectrum.

    Examples
    --------
    Translate a simulated spectrum, moving the offset up:

    >>> from specparam.sim import sim_power_spectrum
    >>> freqs, powers = sim_power_spectrum([1, 50], [1, 1], [10, 0.5, 1])
    >>> translated_powers = translate_spectrum(powers, 0.5)
    """

    translated_spectrum = np.power(10, delta_offset, dtype='float') * power_spectrum

    return translated_spectrum


def rotate_sim_spectrum(freqs, power_spectrum, delta_exponent, f_rotation, sim_params):
    """Rotate a simulated power spectrum, updating a SimParams object.

    Parameters
    ----------
    freqs : 1d array
        Frequency axis of input power spectrum, in Hz.
    power_spectrum : 1d array
        Power values of the spectrum.
    delta_exponent : float
        Change in aperiodic exponent to be applied, where:

        - positive is clockwise rotation (steepen)
        - negative is counterclockwise rotation (flatten)
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.
    sim_params : SimParams
        Object storing the current parameter definitions.

    Returns
    -------
    rotated_spectrum : 1d array
        Rotated power spectrum.
    new_sim_params : SimParams
        New parameter definitions.

    Notes
    -----
    Warning: This function should only be applied to spectra without a knee.
    If using simulated data, this is spectra created in 'fixed' mode.
    This is because the rotation applied is inconsistent with
    the formulation of knee spectra, and will change them in an
    unspecified way, not just limited to doing the rotation.

    Examples
    --------
    Rotate a simulated spectrum, changing the exponent around a rotation point of 25 Hz:

    >>> from specparam.sim import sim_power_spectrum
    >>> freqs, powers, sp = sim_power_spectrum([1, 50], [1, 1], [10, 0.5, 1], return_params=True)
    >>> rotated_powers, new_sp = rotate_sim_spectrum(freqs, powers, 0.5, 25, sp)
    """

    rotated_spectrum = rotate_spectrum(freqs, power_spectrum, delta_exponent, f_rotation)
    delta_offset = compute_rotation_offset(delta_exponent, f_rotation)

    new_sim_params = update_sim_ap_params(sim_params, [delta_offset, delta_exponent])

    return rotated_spectrum, new_sim_params


def translate_sim_spectrum(power_spectrum, delta_offset, sim_params):
    """Translate a simulated spectrum, updating a SimParams object.

    Parameters
    ----------
    power_spectrum : 1d array
        Power values of the spectrum.
    delta_offset : float
        Amount to change the offset by, where:

        - positive values are an upwards translation
        - negative are are a downwards translation
    sim_params : SimParams
        Object storing the current parameter definitions.

    Returns
    -------
    translated_spectrum : 1d array
        Translated power spectrum.
    new_sim_params : SimParams
        New parameter definitions.

    Examples
    --------
    Translate a simulated spectrum, moving the offset up:

    >>> from specparam.sim import sim_power_spectrum
    >>> freqs, powers, sp = sim_power_spectrum([1, 50], [1, 1], [10, 0.5, 1], return_params=True)
    >>> translated_powers, new_sp = translate_sim_spectrum(powers, 0.5, sp)
    """

    translated_spectrum = translate_spectrum(power_spectrum, delta_offset)
    new_sim_params = update_sim_ap_params(sim_params, delta_offset, 'offset')

    return translated_spectrum, new_sim_params


def compute_rotation_offset(delta_exponent, f_rotation):
    """Calculate the change in offset from a given rotation.

    Parameters
    ----------
    delta_exponent : float
        The change in aperiodic exponent value.
    f_rotation : float
        The frequency value, in Hz, where rotation is applied.

    Returns
    -------
    float
        The amount the offset will change for the specified exponent change.

    Examples
    --------
    Calculate the induced change in offset of a change in exponent of 0.5 at 25 Hz:

    >>> delta_offset = compute_rotation_offset(0.5, 25)
    """

    return -np.log10(f_rotation) * -delta_exponent


def compute_rotation_frequency(delta_exponent_b, f_rotation_b, delta_exponent_c, f_rotation_c):
    """Calculate the rotation frequency between two rotated power spectra.

    Parameters
    ----------
    delta_exponent_b : float
        The applied change in exponent value for power spectrum 'B'.
    f_rotation_b : float
        The rotation frequency applied to power spectrum 'B'.
    delta_exponent_c : float
        The applied change in exponent value for power spectrum 'C'.
    f_rotation_c : float
        The rotation frequency applied to power spectrum 'C'.

    Returns
    -------
    float
        The frequency rotation point between spectra 'B' & 'C'.

    Notes
    -----
    **Code Notes**

    This computes the rotation frequency for two power spectra 'B' & 'C',
    under the assumption that they are both rotated versions of a the
    same original power spectrum 'A'.

    **Derivation**

    Given an original power spectrum A, then:

    - B = A*(f_rotation_b/freqs)^delta_exponent_b
    - C = A*(f_rotation_c/freqs)^delta_exponent_c

    Therefore, what you want is f_rotation_bc, which is the frequency where B==C.

    To find this, we can plug everything back into the equation, to find where
    B[freqs] == C[freqs], which is how we arrive at the solution below.

    Examples
    --------
    Calculate the rotation frequency between two transformed power spectra:

    >>> f_rotation = compute_rotation_frequency(0.5, 25, -0.25, 10)
    """

    return (((f_rotation_c**delta_exponent_c) / (f_rotation_b**delta_exponent_b))) ** \
        (1/(delta_exponent_c-delta_exponent_b))
