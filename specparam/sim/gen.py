"""Functions for generating model components."""

import numpy as np

from specparam.core.funcs import get_ap_func, get_pe_func, infer_ap_func

from specparam.sim.transform import rotate_spectrum

###################################################################################################
###################################################################################################

def gen_freqs(freq_range, freq_res):
    """Generate a frequency vector.

    Parameters
    ----------
    freq_range : list of [float, float]
        Frequency range to create frequencies across, as [f_low, f_high], inclusive.
    freq_res : float
        Frequency resolution for the frequency vector.

    Returns
    -------
    freqs : 1d array
        Frequency values, in linear spacing.

    Examples
    --------
    Generate a vector of frequency values from 1 to 50:

    >>> freqs = gen_freqs([1, 50], freq_res=0.5)
    """

    # The end value has something added to it, to make sure the last value is included
    #   It adds a fraction to not accidentally include points beyond range
    #   due to rounding / or uneven division of the freq_res into range to simulate
    freqs = np.arange(freq_range[0], freq_range[1] + (0.5 * freq_res), freq_res)

    return freqs


def gen_aperiodic(freqs, aperiodic_params, aperiodic_mode=None):
    """Generate aperiodic values.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create aperiodic component for.
    aperiodic_params : list of float
        Parameters that define the aperiodic component.
    aperiodic_mode : {'fixed', 'knee'}, optional
        Which kind of aperiodic component to generate.
        If not provided, is inferred from the parameters.

    Returns
    -------
    ap_vals : 1d array
        Aperiodic values, in log10 spacing.
    """

    if not aperiodic_mode:
        aperiodic_mode = infer_ap_func(aperiodic_params)

    ap_func = get_ap_func(aperiodic_mode)

    ap_vals = ap_func(freqs, *aperiodic_params)

    return ap_vals


def gen_periodic(freqs, periodic_params, periodic_mode='gaussian'):
    """Generate periodic values.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create peak values for.
    periodic_params : list of float
        Parameters to create the periodic component.
    periodic_mode : {'gaussian'}, optional
        Which kind of periodic component to generate.

    Returns
    -------
    peak_vals : 1d array
        Peak values, in log10 spacing.
    """

    pe_func = get_pe_func(periodic_mode)

    pe_vals = pe_func(freqs, *periodic_params)

    return pe_vals


def gen_noise(freqs, nlv):
    """Generate noise values for a simulated power spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create noise values for.
    nlv : float
        Noise level to generate.

    Returns
    -------
    noise_vals : 1d vector
        Noise values.

    Notes
    -----
    This approach generates noise as randomly distributed white noise.
    The 'level' of noise is controlled as the scale of the normal distribution.
    """

    noise_vals = np.random.normal(0, nlv, len(freqs))

    return noise_vals


def gen_power_vals(freqs, aperiodic_params, periodic_params, nlv):
    """Generate power values for a simulated power spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create power values for.
    aperiodic_params : list of float
        Parameters to create the aperiodic component of the power spectrum.
    periodic_params : list of float
        Parameters to create the periodic component of the power spectrum.
    nlv : float
        Noise level to add to generated power spectrum.

    Returns
    -------
    powers : 1d vector
        Power values, in linear spacing.

    Notes
    -----
    This function should be used when simulating power spectra, as it:

    - Takes in input parameter definitions as lists, as used for simulating power spectra.
    - Returns the power spectrum in linear spacing, as is used for simulating power spectra.
    """

    ap_vals = gen_aperiodic(freqs, aperiodic_params)
    pe_vals = gen_periodic(freqs, periodic_params)
    noise = gen_noise(freqs, nlv)

    powers = np.power(10, ap_vals + pe_vals + noise)

    return powers


def gen_rotated_power_vals(freqs, aperiodic_params, periodic_params, nlv, f_rotation):
    """Generate power values for a simulated power spectrum, rotated around a given frequency.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create power values for.
    aperiodic_params : list of float
        Parameters to create the aperiodic component of the power spectrum.
    periodic_params : list of float
        Parameters to create the periodic component of the power spectrum.
    nlv : float
        Noise level to add to generated power spectrum.
    f_rotation : float
        Frequency value, in Hz, about which rotation is applied, at which power is unchanged.

    Returns
    -------
    powers : 1d vector
        Power values, in linear spacing.

    Raises
    ------
    ValueError
        If a rotation is requested on a power spectrum with a knee, as this is not supported.
    """

    if len(aperiodic_params) == 3:
        raise ValueError('Cannot rotate power spectra generated with a knee.')

    powers = gen_power_vals(freqs, [0, 0], periodic_params, nlv)
    powers = rotate_spectrum(freqs, powers, aperiodic_params[1], f_rotation)

    return powers


def gen_model(freqs, aperiodic_params, periodic_params, return_components=False):
    """Generate a power spectrum model for a given parameter definition.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create the model for.
    aperiodic_params : 1d array
        Parameters to create the aperiodic component of the modeled power spectrum.
    periodic_params : 2d array
        Parameters to create the periodic component of the modeled power spectrum.
    return_components : bool, optional, default: False
        Whether to also return the components of the model.

    Returns
    -------
    full_model : 1d array
        The full power spectrum model, in log10 spacing.
    pe_fit : 1d array
        The periodic component of the model, containing the peaks.
        Only returned if `return_components` is True.
    ap_fit : 1d array
        The aperiodic component of the model.
        Only returned if `return_components` is True.

    Notes
    -----
    This function should be used when computing model reconstructions, as it:

    - Takes in input parameter definitions as arrays, as used in model objects.
    - Returns the power spectrum in log10 spacing, as is used in model models.
    """

    ap_fit = gen_aperiodic(freqs, aperiodic_params)
    pe_fit = gen_periodic(freqs, np.ndarray.flatten(periodic_params))
    full_model = pe_fit + ap_fit

    if return_components:
        return full_model, pe_fit, ap_fit
    else:
        return full_model
