"""Synthesis functions for generating model components and synthetic power spectra."""

from inspect import isgenerator
from collections import namedtuple
from itertools import chain, repeat

import numpy as np

from fooof.core.utils import group_three
from fooof.core.funcs import gaussian_function, get_bg_func, infer_bg_func

###################################################################################################
###################################################################################################

SynParams = namedtuple('SynParams', ['background_params', 'gaussian_params', 'nlv'])

class Stepper():
    """Object for stepping across parameter values.

    Parameters
    ----------
    start : float
        Start value to iterate from.
    stop : float
        End value to iterate to.
    step : float
        Incremet of each iteration.

    Attributes
    ----------
    len : int
        Length of generator range.
    data : iterator
        Set of specified parameters to iterate across.
    """

    def __init__(self, start, stop, step):

        self._check_values(start, stop, step)

        self.start = start
        self.stop = stop
        self.step = step
        self.len = int((stop-start)/step)
        self.data = iter(np.arange(start, stop, step))


    def __len__(self):

        return self.len


    def __next__(self):

        return round(next(self.data), 4)


    def __iter__(self):

        return self.data


    @staticmethod
    def _check_values(start, stop, step):
        """Checks if provided values are valid for use."""

        if any(i < 0 for i in [start, stop, step]):
            raise ValueError("'start', 'stop', and 'step' should all be positive values")

        if not start < stop:
            raise ValueError("'start' should be less than stop")

        if not step < (stop - start):
            raise ValueError("'step' is too large given 'start' and 'stop' values")


def param_iter(params):
    """Generates parameters to iterate over.

    Parameters
    ----------
    params : list of floats and Stepper
        Parameters over which to iterate, where:
            Stepper object defines iterated parameter and its range and,
            floats are other parameters that will be held constant.

    Yields
    ------
    list of floats
        Next generated list of parameters.

    Example
    -------
    Iterates over center frequency values from 8 to 12 in increments of .25.
    >>> osc = param_iter([Stepper(8, 12, .25), 1, 1])
    """

    # If input is a list of lists, check each element, and flatten if needed
    if isinstance(params[0], list):
        params = [item for sublist in params for item in sublist]

    # Finds where Stepper object is. If there is more than one, raise an error
    iter_ind = 0
    num_iters = 0
    for cur_ind, param in enumerate(params):
        if isinstance(param, Stepper):
            num_iters += 1
            iter_ind = cur_ind

        if num_iters > 1:
            raise ValueError("Iteration is only supported on one parameter")

    # Generate and yield next set of parameters
    gen = params[iter_ind]
    while True:
        try:
            params[iter_ind] = next(gen)
            yield params
        except StopIteration:
            return


def param_sampler(params, probs=None):
    """Makes a generator to sample randomly from possible parameters.

    Parameters
    ----------
    params : list of lists or list of float
        Possible parameter values.
    probs : list of float, optional
        Probabilities with which to sample each parameter option. Default: None
            If None, each parameter option is sampled uniformly.

    Yields
    ------
    obj
        A randomly sampled element from params.
    """

    # If input is a list of lists, check each element, and flatten if needed
    if isinstance(params[0], list):
        params = [_check_flat(lst) for lst in params]

    # In order to use numpy's choice, with probabilities, choices are made on indices
    # This is because the params can be a messy-sized list, that numpy choice does not like
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
            Positive is counterclockwise rotation (flatten)
            Negative is clockwise rotation (steepen).
    f_rotation : float
        Frequency, in Hz, at which to do the rotation, such that power at that frequency is unchanged.

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

    # If object is not a generator, update to become one
    #   Otherwise (if the object already is a generator) then it gets left as it is
    if not isgenerator(obj):

        if isinstance(obj, list):

            # Check if it's an empty list, if so make it a repeat generator of empty lists
            if len(obj) == 0:
                obj = repeat(obj)

            # If obj is a list of lists of the right length, then we will leave it as is:
            #   as a list of list that will iterate through each element
            # If it is not, then it's turned into a repeat generator
            # Note: checks that it's a list to not have an implicit error
            #   when it's a list of numbers, that happens to be same length as n_spectra
            elif not (isinstance(obj[0], list) and len(obj) == length):
                obj = repeat(obj)

        # If it's not a list, make it a repeat object (repeat int/float)
        else:
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

    Notes
    -----
    This function only deals with one level of nesting.
    """

    # Note: flatten if list contains list(s), but skip if list is empty (which is valid)
    if len(lst) != 0 and isinstance(lst[0], list):
        lst = list(chain(*lst))

    return lst
