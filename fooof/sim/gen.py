"""Functions for generating model components and simulated power spectra."""

import numpy as np

from fooof.core.utils import group_three, check_iter, check_flat
from fooof.core.funcs import gaussian_function, get_ap_func, infer_ap_func
from fooof.sim.params import SimParams

###################################################################################################
###################################################################################################

def gen_freqs(freq_range, freq_res):
    """Generate a frequency vector.

    Parameters
    ----------
    freq_range : list of [float, float]
        Frequency range of desired frequency vector, as [f_low, f_high], inclusive.
    freq_res : float
        Frequency resolution of desired frequency vector.

    Returns
    -------
    freqs : 1d array
        Frequency values, in linear space.
    """

    # The end value has something added to it, to make sure the last value is included
    #   It adds a fraction to not accidentally include points beyond range
    #   due to rounding / or uneven division of the freq_res into range to simulate
    freqs = np.arange(freq_range[0], freq_range[1] + (0.5 * freq_res), freq_res)

    return freqs


def gen_power_spectrum(freq_range, aperiodic_params, gaussian_params, nlv=0.005, freq_res=0.5):
    """Generate a simualted power spectrum.

    Parameters
    ----------
    freq_range : list of [float, float]
        Minimum and maximum values of the desired frequency vector.
    aperiodic_params : list of float
        Parameters to create the aperiodic component of a power spectrum. Length of 2 or 3 (see note).
    gaussian_params : list of float or list of list of float
        Parameters to create peaks. Total length of n_peaks * 3 (see note).
    nlv : float, optional, default: 0.005
        Noise level to add to generated power spectrum.
    freq_res : float, optional, default: 0.5
        Frequency resolution for the simulated power spectrum.

    Returns
    -------
    freqs : 1d array
        Frequency values, in linear space.
    powers : 1d array
        Power values, in linear space.

    Notes
    -----
    Aperiodic Parameters:

    - The function for the aperiodic process to use is inferred from the provided parameters.
    - If length of 2, the 'fixed' aperiodic mode is used, if length of 3, 'knee' is used.

    Gaussian Parameters:

    - Each gaussian description is a set of three values:

      * mean (Center Frequency), height (Power), and standard deviation (Bandwidth).
      * Make sure any center frequencies you request are within the simulated frequency range

    - The total number of parameters that need to be specified is number of peaks * 3

      * These can be specified in as all together in a flat list (ex: [10, 1, 1, 20, 0.5, 1])
      * They can also be grouped into a list of lists (ex: [[10, 1, 1], [20, 0.5, 1]])

    Examples
    --------
    Generate a power spectrum with a single peak, at 10 Hz:

    >>> freqs, psd = gen_power_spectrum([1, 50], [0, 2], [10, 1, 1])

    Generate a power spectrum with alpha and beta peaks:

    >>> freqs, psd = gen_power_spectrum([1, 50], [0, 2], [[10, 1, 1], [20, 0.5, 1]])
    """

    freqs = gen_freqs(freq_range, freq_res)
    powers = gen_power_vals(freqs, aperiodic_params, check_flat(gaussian_params), nlv)

    return freqs, powers


def gen_group_power_spectra(n_spectra, freq_range, aperiodic_params,
                            gaussian_params, nlvs=0.005, freq_res=0.5):
    """Generate a group of simulated power spectra.

    Parameters
    ----------
    n_spectra : int
        The number of power spectra to generate in the matrix.
    freq_range : list of [float, float]
        Minimum and maximum values of the desired frequency vector.
    aperiodic_params : list of float or generator
        Parameters for the aperiodic component of the power spectra.
    gaussian_params : list of float or generator
        Parameters for the peaks of the power spectra.
            Length of n_peaks * 3.
    nlvs : float or list of float or generator, optional, default: 0.005
        Noise level to add to generated power spectrum.
    freq_res : float, optional, default: 0.5
        Frequency resolution for the simulated power spectra.

    Returns
    -------
    freqs : 1d array
        Frequency values (linear).
    powers : 2d array
        Matrix of power values (linear), as [n_power_spectra, n_freqs].
    sim_params : list of SimParams
        Definitions of parameters used for each spectrum. Has length of n_spectra.

    Notes
    -----
    Parameters options can be:

    - A single set of parameters.
      If so, these same parameters are used for all spectra.
    - A list of parameters whose length is n_spectra.
      If so, each successive parameter set is such for each successive spectrum.
    - A generator object that returns parameters for a power spectrum.
      If so, each spectrum has parameters pulled from the generator.

    Aperiodic Parameters:

    - The function for the aperiodic process to use is inferred from the provided parameters.
    - If length of 2, the 'fixed' aperiodic mode is used, if length of 3, 'knee' is used.

    Gaussian Parameters:

    - Each gaussian description is a set of three values:

      * mean (Center Frequency), height (Power), and standard deviation (Bandwidth).
      * Make sure any center frequencies you request are within the simulated frequency range.

    Examples
    --------
    Generate 2 power spectra using the same parameters:

    >>> freqs, psds, _ = gen_group_power_spectra(2, [1, 50], [0, 2], [10, 1, 1])

    Generate 10 power spectra, randomly sampling possible parameters:

    >>> ap_opts = param_sampler([[0, 1.0], [0, 1.5], [0, 2]])
    >>> gauss_opts = param_sampler([[], [10, 1, 1], [10, 1, 1, 20, 2, 1]])
    >>> freqs, psds, sim_params = gen_group_power_spectra(10, [1, 50], ap_opts, gauss_opts)
    """

    # Initialize things
    freqs = gen_freqs(freq_range, freq_res)
    powers = np.zeros([n_spectra, len(freqs)])
    sim_params = [None] * n_spectra

    # Check if inputs are generators, if not, make them into repeat generators
    aperiodic_params = check_iter(aperiodic_params, n_spectra)
    gaussian_params = check_iter(gaussian_params, n_spectra)
    nlvs = check_iter(nlvs, n_spectra)

    # Simulate power spectra
    for ind, bgp, gp, nlv in zip(range(n_spectra), aperiodic_params, gaussian_params, nlvs):

        sim_params[ind] = SimParams(bgp.copy(), sorted(group_three(gp)), nlv)
        powers[ind, :] = gen_power_vals(freqs, bgp, gp, nlv)

    return freqs, powers, sim_params


def gen_aperiodic(freqs, aperiodic_params, aperiodic_mode=None):
    """Generate aperiodic values, from parameter definition.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create aperiodic component for.
    aperiodic_params : list of float
        Parameters that define the aperiodic component.
    aperiodic_mode : {'fixed', 'knee'}, optional
        Which kind of aperiodic component to generate power spectra with.
        If not provided, is infered from the parameters.

    Returns
    -------
    ap_vals : 1d array
        Generated aperiodic values.
    """

    if not aperiodic_mode:
        aperiodic_mode = infer_ap_func(aperiodic_params)

    ap_func = get_ap_func(aperiodic_mode)

    ap_vals = ap_func(freqs, *aperiodic_params)

    return ap_vals


def gen_peaks(freqs, gaussian_params):
    """Generate peaks values, from parameter definition.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create peak values from.
    gaussian_params : list of float
        Parameters to create peaks. Length of n_peaks * 3.

    Returns
    -------
    peak_vals : 1d array
        Generated aperiodic values.
    """

    peak_vals = gaussian_function(freqs, *gaussian_params)

    return peak_vals


def gen_power_vals(freqs, aperiodic_params, gaussian_params, nlv):
    """Generate power values for a power spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency vector to create power values from.
    aperiodic_params : list of float
        Parameters to create the aperiodic component of the power spectrum.
    gaussian_params : list of float
        Parameters to create peaks. Length of n_peaks * 3.
    nlv : float
        Noise level to add to generated power spectrum.

    Returns
    -------
    powers : 1d vector
        Power values (linear).
    """

    aperiodic = gen_aperiodic(freqs, aperiodic_params)
    peaks = gen_peaks(freqs, gaussian_params)
    noise = np.random.normal(0, nlv, len(freqs))

    powers = np.power(10, aperiodic + peaks + noise)

    return powers
