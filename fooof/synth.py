"""Synthesis functions for generating model components and synthetic power spectra."""

from random import choice
from itertools import chain, repeat
from collections import namedtuple

import numpy as np

from fooof.core.utils import group_three
from fooof.core.funcs import gaussian_function, get_bg_func, infer_bg_func

###################################################################################################
###################################################################################################

SynParams = namedtuple('SynParams', ['background_params', 'gaussian_params', 'nlv'])

def param_sampler(params, probs=None):
    """Make a generator to sample randomly from possible params.

    Parameters
    ----------
    params : list
        Possible parameter values.
    probs : list of float, optional
        Probabilities with which to sample each parameter option. Default: None
            If None, each parameter option is sampled uniformly.

    Yields
    ------
    obj
        A randomly sampled element from params.
    """

    # In order to use numpy's choice, with probabilities, choices are made on indices
    #  This is because the params can be a messy-sized list, that numpy choice does not like
    inds = np.array(range(len(params)))

    # While loop allows the generator to be called an arbitrary number of times.
    while True:
        yield params[np.random.choice(inds, p=probs)]


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
            - mean (CF), amplitude (Amp), and std (BW)
        - The total number of parameters that need to be specified is number of peaks * 3
            - These can be specified in as all together in a flat list.
                - For example: [10, 1, 1, 20, 0.5, 1]
            - They can also be grouped into a list of lists
                - For example: [[10, 1, 1], [20, 0.5, 1]]
    """

    xs = gen_freqs(freq_range, freq_res)
    ys = gen_power_vals(xs, background_params, _check_flat(gauss_params), nlv)

    return xs, ys


def gen_group_power_spectra(n_spectra, freq_range, background_params, gauss_params, nlvs=0.005, freq_res=0.5):
    """Generate a group of synthetic power spectra.

    Parameters
    ----------
    n_spectra : int
        The number of power spectra to generate in the matrix.
    freq_range : list of [float, float]
        Minimum and maximum values of the desired frequency vector.
    background_params : list of float or generator
        Parameter for the background of the power spectra.
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
        Matrix of power values (linear).
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
            - mean (CF), amplitude (Amp), and std (BW)
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

        syn_params[ind] = SynParams(bgp, sorted(group_three(gp)), nlv)
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

###################################################################################################
###################################################################################################

def _check_iter(obj, length):
    """Check an object to ensure that it is iterable, and make it iterable if not.

    Parameters
    ----------
    obj : generator or list or float
        Object to check status of.
    length : int
        The (minimum) length the iterator needs to be.

    Returns
    -------
    obj : generator
        Iterable object.
    """

    # If object is a generator, leave as is
    try:
        next(obj)

    # If next fails, it's not a generator
    except TypeError:

        # If it's a list, make it a repeat generator
        #  Unless it's the right length, then it will iterate through each element
        try:
            if len(obj) != length:
                obj = repeat(obj)

        # If it is not a list (for example, float), make it a repeat generator
        except:
            obj = repeat(obj)

    return obj


def _check_flat(lst):
    """Check whether a list is flat, and flatten if not.

    Parameters
    ----------
    lst : list or list of lists
        A list object to be checked and potentially flattened.

    Returns
    -------
    list
        A '1D' list, which is a flattened version of the input.
    """

    if isinstance(lst[0], list):
        lst = list(chain(*lst))

    return lst
