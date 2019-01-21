"""Synthesis functions for generating model components and synthetic power spectra."""

import numpy as np

from fooof.core.utils import group_three
from fooof.core.funcs import gaussian_function, get_bg_func, infer_bg_func
from fooof.synth.utils import _check_iter, _check_flat
from fooof.synth.params import SynParams

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
        Parameters to create the background of a power spectrum. Length of 2 or 3 (see note).
    gauss_params : list of float or list of list of float
        Parameters to create peaks. Total length of n_peaks * 3 (see note).
    nlv : float, optional
        Noise level to add to generated power spectrum. Default: 0.005
    freq_res : float, optional
        Frequency resolution for the synthetic power spectra. Default: 0.5

    Returns
    -------
    xs : 1d array
        Frequency values (linear).
    ys : 1d array
        Power values (linear).

    Notes
    -----
    Background Parameters:
        - The type of background process to use is inferred from the provided parameters.
            - If length of 2, the 'fixed' background is used, if length of 3, 'knee' is used.
    Gaussian Parameters:
        - Each gaussian description is a set of three values:
            - mean (Center Frequency), amplitude (Amplitude), and std (Bandwidth)
            - Make sure any center frequencies you request are within the simulated frequency range
        - The total number of parameters that need to be specified is number of peaks * 3
            - These can be specified in as all together in a flat list.
                - For example: [10, 1, 1, 20, 0.5, 1]
            - They can also be grouped into a list of lists
                - For example: [[10, 1, 1], [20, 0.5, 1]]

    Examples
    --------

    Generate a power spectrum with a single

    >>> freqs, psd = gen_power_spectrum([1, 50], [0, 2], [10, 1, 1])

    Generate a power spectrum with alpha and beta peaks

    >>> freqs, psd = gen_power_spectrum([1, 50], [0, 2], [[10, 1, 1], [20, 0.5, 1]])
    """

    xs = gen_freqs(freq_range, freq_res)
    ys = gen_power_vals(xs, background_params, _check_flat(gauss_params), nlv)

    return xs, ys


def gen_group_power_spectra(n_spectra, freq_range, background_params,
                            gauss_params, nlvs=0.005, freq_res=0.5):
    """Generate a group of synthetic power spectra.

    Parameters
    ----------
    n_spectra : int
        The number of power spectra to generate in the matrix.
    freq_range : list of [float, float]
        Minimum and maximum values of the desired frequency vector.
    background_params : list of float or generator
        Parameters for the background of the power spectra.
    gauss_params : list of float or generator
        Parameters for the peaks of the power spectra.
            Length of n_peaks * 3.
    nlvs : float or list of float or generator, optional
        Noise level to add to generated power spectrum. default: 0.005
    freq_res : float, optional
        Frequency resolution for the synthetic power spectra. default: 0.5

    Returns
    -------
    xs : 1d array
        Frequency values (linear).
    ys : 2d array
        Matrix of power values (linear), as [n_power_spectra, n_freqs].
    syn_params : list of SynParams
        Definitions of parameters used for each spectrum. Has length of n_spectra.

    Notes
    -----
    Parameters options can be:
        - A single set of parameters
            - If so, these same parameters are used for all spectra.
        - A list of parameters whose length is n_spectra.
            - If so, each successive parameter set is such for each successive spectrum.
        - A generator object that returns parameters for a power spectrum.
            - If so, each spectrum has parameters pulled from the generator.
    Background Parameters:
        - The type of background process to use is inferred from the provided parameters.
            - If length of 2, 'fixed' background is used, if length of 3, 'knee' is used.
    Gaussian Parameters:
        - Each gaussian description is a set of three values:
            - mean (Center Frequency), amplitude (Amplitude), and std (Bandwidth)
            - Make sure any center frequencies you request are within the simulated frequency range

    Examples
    --------
    Generate 2 power spectra using the same parameters.
    >>> freqs, psds, _ = gen_group_power_spectra(2, [1, 50], [0, 2], [10, 1, 1])

    Generate 10 power spectra, randomly sampling possible parameters
    >>> bg_opts = param_sampler([[0, 1.0], [0, 1.5], [0, 2]])
    >>> gauss_opts = param_sampler([[], [10, 1, 1], [10, 1, 1, 20, 2, 1]])
    >>> freqs, psds, syn_params = gen_group_power_spectra(10, [1, 50], bg_opts, gauss_opts)
    """

    # Initialize things
    xs = gen_freqs(freq_range, freq_res)
    ys = np.zeros([n_spectra, len(xs)])
    syn_params = [None] * n_spectra

    # Check if inputs are generators, if not, make them into repeat generators
    background_params = _check_iter(background_params, n_spectra)
    gauss_params = _check_iter(gauss_params, n_spectra)
    nlvs = _check_iter(nlvs, n_spectra)

    # Synthesize power spectra
    for ind, bgp, gp, nlv in zip(range(n_spectra), background_params, gauss_params, nlvs):

        syn_params[ind] = SynParams(bgp.copy(), sorted(group_three(gp)), nlv)
        ys[ind, :] = gen_power_vals(xs, bgp, gp, nlv)

    return xs, ys, syn_params


def gen_background(xs, background_params, background_mode=None):
    """Generate background values, from parameter definition.

    Parameters
    ----------
    xs : 1d array
        Frequency vector to create background from.
    background_params : list of float
        Parameters that define the background process.
    background_mode : {'fixed', 'knee'}, optional
        Which kind of background to generate power spectra with.
            If not provided, is infered from the parameters.

    Returns
    -------
    1d array
        Generated background values.
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
    gauss_params : list of float
        Parameters to create peaks. Length of n_peaks * 3.

    Returns
    -------
    1d array
        Generated background values.
    """

    return gaussian_function(xs, *gauss_params)


def gen_power_vals(xs, background_params, gauss_params, nlv):
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

    background = gen_background(xs, background_params)
    peaks = gen_peaks(xs, gauss_params)
    noise = np.random.normal(0, nlv, len(xs))

    ys = np.power(10, background + peaks + noise)

    return ys
