"""Functions for generating model components and simulated power spectra."""

import numpy as np

from ERPparam.core.utils import check_iter
from ERPparam.core.funcs import  get_pe_func

from ERPparam.sim.params import collect_sim_params

###################################################################################################
###################################################################################################

def gen_time_vector(time_range, fs):
    """Generate a frequency vector.

    Parameters
    ----------
    time_range : list of [float, float]
        Time range to create time vector across, as [start_time, end_time], inclusive.
    fs : float
        Sampling frequency for desired time vector.

    Returns
    -------
    time : 1d array
        Time values.

    Examples
    --------
    Generate a vector of time values from -1 to 1:

    >>> time = gen_time_vector([-1, 1], fs=2000)
    """

    # The end value has something added to it, to make sure the last value is included
    #   It adds a fraction to not accidentally include points beyond range
    #   due to rounding / or uneven division of the fs into range to simulate
    time = np.arange(time_range[0], time_range[1] + (0.5 / fs), (1/fs))

    return time


def gen_power_spectrum(time_range,  periodic_params, nlv=0.005, fs=1000, return_params=False):
    """Generate a simulated power spectrum.

    Parameters
    ----------
    time_range : list of [float, float]
        Time range to create time vector across, as [start_time, end_time], inclusive.
    periodic_params : list of float or generator
        Parameters for the periodic component of the power spectra.
        Length of n_peaks * 3.
    nlvs : float or list of float or generator, optional, default: 0.005
        Noise level to add to generated power spectrum.
    fs : float
        Sampling frequency for desired time vector.
    return_params : bool, optional, default: False
        Whether to return the parameters for the simulated spectra.

    Returns
    -------
    time : 1d array
        Time vector.
    signals : 2d array
        Matrix of signals [n_signals, n_times].
    sim_params : list of SimParams
        Definitions of parameters used for each signal. Has length of n_signals.
        Only returned if `return_params` is True.
    """

    time = gen_time_vector(time_range, fs)
    signal = gen_signal(time, periodic_params, nlv)

    if return_params:
        sim_params = collect_sim_params(periodic_params, nlv)
        return time, signal, sim_params
    else:
        return time, signal



def gen_group_power_spectra(n_spectra, time_range, periodic_params, nlvs=0.005,
                            fs=1000, return_params=False):
    """Generate a group of simulated power spectra.

    Parameters
    ----------
    n_spectra : int
        The number of power spectra to generate.
    time_range : list of [float, float]
        Time range to create time vector across, as [start_time, end_time], inclusive.
    periodic_params : list of float or generator
        Parameters for the periodic component of the power spectra.
        Length of n_peaks * 3.
    nlvs : float or list of float or generator, optional, default: 0.005
        Noise level to add to generated power spectrum.
    fs : float
        Sampling frequency for desired time vector.
    return_params : bool, optional, default: False
        Whether to return the parameters for the simulated spectra.

    Returns
    -------
    time : 1d array
        Time vector.
    signals : 2d array
        Matrix of signals [n_signals, n_times].
    sim_params : list of SimParams
        Definitions of parameters used for each signal. Has length of n_signals.
        Only returned if `return_params` is True.
    """

    # Initialize things
    time = gen_time_vector(time_range, fs)
    signals = np.zeros([n_spectra, len(time)])
    sim_params = [None] * n_spectra

    # Check if inputs are generators, if not, make them into repeat generators
    pe_params = check_iter(periodic_params, n_spectra)
    nlvs = check_iter(nlvs, n_spectra)

    # Simulate power spectra
    for ind, pe, nlv in zip(range(n_spectra), pe_params, nlvs):
        signals[ind, :] = gen_signal(time, pe, nlv)

        sim_params[ind] = collect_sim_params(pe, nlv)

    if return_params:
        return time, signals, sim_params
    else:
        return time, signals


def gen_periodic(time, periodic_params, periodic_mode='gaussian'):
    """Generate periodic values.

    Parameters
    ----------
    time : 1d array
        Time vector to create peak values for.
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

    pe_vals = pe_func(time, *periodic_params)

    return pe_vals


def gen_noise(time, nlv):
    """Generate noise values for a simulated power spectrum.

    Parameters
    ----------
    time : 1d array
        Time vector to create noise values for.
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

    noise_vals = np.random.normal(0, nlv, len(time))

    return noise_vals


def gen_signal(time, periodic_params, nlv):
    """Generate simulated ERP.

    Parameters
    ----------
    time : 1d array
        Time vector to create power values for.
    periodic_params : list of float
        Parameters to create the periodic component of the signal.
    nlv : float
        Noise level to add to generated signal.

    Returns
    -------
    signal : 1d vector
        simulated signal.

    """

    pe_vals = gen_periodic(time, periodic_params)
    noise = gen_noise(time, nlv)

    signal = pe_vals + noise

    return signal
