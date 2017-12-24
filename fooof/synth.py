"""Synthesis functions for generating model components and synthetic power spectra."""

import numpy as np

from fooof.core.funcs import gaussian_function, get_bg_func, infer_bg_func

###################################################################################################
###################################################################################################

def gen_freqs(freq_range, freq_res):
    """Generate a frequency vector, from the frequency range and resolution.

    Parameters
    ----------
    freq_range : list of [float, float]
        Frequency range of desired frequency vector, as [f_low, f_high].
    freq_res : float
        Frequency resolution of desired frequency vector.

    Returns
    -------
    1d array
        Frequency values (linear).
    """

    return np.arange(freq_range[0], freq_range[1]+freq_res, freq_res)


def gen_power_spectrum(freq_range, background_params, gauss_params, nlv=0.005, freq_res=0.5):
    """Generate a synthetic power spectrum.

    Parameters
    ----------
    freq_range : list of [float, float]
        Minimum and maximum values of the desired frequency vector.
    background_params : list of float
        Parameters to create the background of a power spectrum.
    gauss_params : list of list of float
        Parameters to create peaks. Length of n_peaks * 3.
    nlv : float, optional
        Noise level to add to generated power spectrum. Default: 0.005
    freq_res : float, optional
        Frequency resolution for the synthetic power spectra.

    Returns
    -------
    xs : 1d array
        Frequency values (linear).
    ys : 1d array
        Power values (linear).

    Notes
    -----
    - The type of background process to use is inferred from the provided parameters.
        - If length of 2, 'fixed' background is used, if length of 3, 'knee' is used.
    """

    xs = gen_freqs(freq_range, freq_res)
    ys = _gen_power_vals(xs, background_params, gauss_params, nlv)

    return xs, ys


def gen_group_power_spectra(n_spectra, freq_range, bgp_opts, gauss_opts, nlv=0.005, freq_res=0.5):
    """Generate a group of synthetic power spectra.

    Parameters
    ----------
    n_spectra : int
        The number of power spectra to generate in the matrix.
    freq_range : list of [float, float]
        Minimum and maximum values of the desired frequency vector.
    background_opts : list of list of float
        Group of parameter sets to create the background of power spectrum.
    gauss_opts : list of of list of float
        Group of parameters sets to create peaks. Length of n_peaks * 3.
    nlv : float, optional
        Noise level to add to generated power spectrum. default: 0.005
    freq_res : float, optional
        Frequency resolution for the synthetic power spectra. default: 0.5

    Returns
    -------
    xs : 1d array
        Frequency values (linear).
    ys : 2d array
        Matrix of power values (linear).

    Notes
    -----
    - Paramaters options can contain more than one parameter description.
        - If so, for each power spectrum, parameters are randomly chosen from the options.
    - The type of background process to use is inferred from the provided parameters.
        - If length of 2, 'fixed' background is used, if length of 3, 'knee' is used.
    """

    xs = gen_freqs(freq_range, freq_res)

    ys = np.zeros([n_spectra, len(xs)])

    for ind in range(n_spectra):

        # Randomly select parameters from options to use for power spectrum
        bg_params = bgp_opts[np.random.randint(0, len(bgp_opts))]
        gauss_params = gauss_opts[np.random.randint(0, len(gauss_opts))]

        ys[ind, :] = _gen_power_vals(xs, bg_params, gauss_params, nlv)

    return xs, ys


def gen_background(xs, background_params, background_mode=None):
    """Generate background values, from parameter definition.

    Parameters
    ----------
    xs : 1d array
        Frequency vector to create background from.
    background_params : list of float
        Paramters that define the background process.
    background_mode : {'fixed', 'knee'}, optional
        Which kind of background to generate power spectra with.
            If not provided, is infered from the parameters.

    Returns
    -------
    1d array
        Generated background values
    """

    if not background_mode:
        background_mode = infer_bg_func(background_params)

    bg_func = get_bg_func(background_mode)

    return bg_func(xs, *background_params)


def gen_peaks(xs, gauss_params):
    """Generate peaks values, from parameter definition.

    Parameters
    ----------
    xs : 1d array
        Frequency vector to create peak values from.
    gauss_params : list of list of float
        Parameters to create peaks. Length of n_peaks * 3.

    Returns
    -------
    1d array
        Generated background values.
    """

    return gaussian_function(xs, *gauss_params)


def _gen_power_vals(xs, bg_params, gauss_params, nlv):
    """Generate power values for a power spectrum.

    Parameters
    ----------
    xs : 1d array
        Frequency vector to create power values from.
    background_params : list of float
        Parameters to create the background of power spectrum.
    gauss_params : list of float
        Parameters to create peaks. Length of n_peaks * 3.
    nlv : float
        Noise level to add to generated power spectrum.

    Returns
    -------
    ys : 1d vector
        Power values (linear).
    """

    background = gen_background(xs, bg_params, infer_bg_func(bg_params))
    peaks = gen_peaks(xs, gauss_params)
    noise = np.random.normal(0, nlv, len(xs))

    ys = np.power(10, background + peaks + noise)

    return ys
