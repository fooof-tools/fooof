"""Functions for simulating power spectra."""

import numpy as np

from specparam.utils.checks import check_iter, check_flat
from specparam.modutils.docs import (docs_get_section, replace_docstring_sections,
                                     docs_replace_param)
from specparam.sim.params import collect_sim_params
from specparam.sim.gen import gen_freqs, gen_power_vals, gen_rotated_power_vals
from specparam.sim.transform import compute_rotation_offset

###################################################################################################
###################################################################################################

def sim_power_spectrum(freq_range, aperiodic_params, periodic_params, nlv=0.005,
                       freq_res=0.5, f_rotation=None, return_params=False):
    """Simulate a power spectrum.

    Parameters
    ----------
    freq_range : list of [float, float]
        Frequency range to simulate power spectrum across, as [f_low, f_high], inclusive.
    aperiodic_params : list of float
        Parameters to create the aperiodic component of a power spectrum.
        Length should be 2 or 3 (see note).
    periodic_params : list of float or list of list of float
        Parameters to create the periodic component of a power spectrum.
        Total length of n_peaks * 3 (see note).
    nlv : float, optional, default: 0.005
        Noise level to add to generated power spectrum.
    freq_res : float, optional, default: 0.5
        Frequency resolution for the simulated power spectrum.
    f_rotation : float, optional
        Frequency value, in Hz, to rotate around.
        Should only be set if spectrum is to be rotated.
    return_params : bool, optional, default: False
        Whether to return the parameters for the simulated spectrum.

    Returns
    -------
    freqs : 1d array
        Frequency values, in linear spacing.
    powers : 1d array
        Power values, in linear spacing.
    sim_params : SimParams
        Definition of parameters used to create the spectrum.
        Only returned if `return_params` is True.

    Notes
    -----
    Aperiodic Parameters:

    - The function for the aperiodic process to use is inferred from the provided parameters.
    - If length of 2, the 'fixed' aperiodic mode is used, if length of 3, 'knee' is used.

    Periodic Parameters:

    - The periodic component is comprised of a set of 'peaks', each of which is described as:

      * Mean (Center Frequency), height (Power), and standard deviation (Bandwidth).
      * Make sure any center frequencies you request are within the simulated frequency range.

    - The total number of parameters that need to be specified is number of peaks * 3

      * These can be specified in as all together in a flat list (ex: [10, 1, 1, 20, 0.5, 1])
      * They can also be grouped into a list of lists (ex: [[10, 1, 1], [20, 0.5, 1]])

    Rotating Power Spectra:

    - You can optionally specify a rotation frequency, such that power spectra will be
      simulated and rotated around that point to the specified aperiodic exponent.

      * This can be used so that any power spectra simulated with the same 'f_rotation'
        will relate to each other by having the specified rotation point.

    - Note that rotating power spectra changes the offset.

      * If you specify an offset value to simulate as well as 'f_rotation', the returned
        spectrum will NOT have the requested offset. It instead will have the offset
        value required to create the requested aperiodic exponent with the requested
        rotation point.
      * If you return SimParams, the recorded offset will be the calculated offset
        of the data post rotation, and not the entered value.

    - You cannot rotate power spectra simulated with a knee.

      * The procedure we use to rotate does not support spectra with a knee, and so
        setting 'f_rotation' with a knee will lead to an error.

    Examples
    --------
    Generate a power spectrum with a single peak, at 10 Hz:

    >>> freqs, powers = sim_power_spectrum([1, 50], [0, 2], [10, 0.5, 1])

    Generate a power spectrum with alpha and beta peaks:

    >>> freqs, powers = sim_power_spectrum([1, 50], [0, 2], [[10, 0.5, 1], [20, 0.5, 1]])

    Generate a power spectrum, that was rotated around a particular frequency point:

    >>> freqs, powers = sim_power_spectrum([1, 50], [None, 2], [10, 0.5, 1], f_rotation=15)
    """

    freqs = gen_freqs(freq_range, freq_res)

    if f_rotation:

        powers = gen_rotated_power_vals(freqs, aperiodic_params,
                                        check_flat(periodic_params), nlv, f_rotation)

        # The rotation changes the offset, so recalculate it's value & update params
        new_offset = compute_rotation_offset(aperiodic_params[1], f_rotation)
        aperiodic_params = [new_offset, aperiodic_params[1]]

    else:

        powers = gen_power_vals(freqs, aperiodic_params, check_flat(periodic_params), nlv)

    if return_params:
        sim_params = collect_sim_params(aperiodic_params, periodic_params, nlv)
        return freqs, powers, sim_params
    else:
        return freqs, powers


def sim_group_power_spectra(n_spectra, freq_range, aperiodic_params, periodic_params, nlvs=0.005,
                            freq_res=0.5, f_rotation=None, return_params=False):
    """Simulate multiple power spectra.

    Parameters
    ----------
    n_spectra : int
        The number of power spectra to generate.
    freq_range : list of [float, float]
        Frequency range to simulate power spectra across, as [f_low, f_high], inclusive.
    aperiodic_params : list of float or generator
        Parameters for the aperiodic component of the power spectra.
    periodic_params : list of float or generator
        Parameters for the periodic component of the power spectra.
        Length of n_peaks * 3.
    nlvs : float or list of float or generator, optional, default: 0.005
        Noise level to add to generated power spectrum.
    freq_res : float, optional, default: 0.5
        Frequency resolution for the simulated power spectra.
    f_rotation : float, optional
        Frequency value, in Hz, to rotate around.
        Should only be set if spectra are to be rotated.
    return_params : bool, optional, default: False
        Whether to return the parameters for the simulated spectra.

    Returns
    -------
    freqs : 1d array
        Frequency values, in linear spacing.
    powers : 2d array
        Matrix of power values, in linear spacing, as [n_power_spectra, n_freqs].
    sim_params : list of SimParams
        Definitions of parameters used for each spectrum. Has length of n_spectra.
        Only returned if `return_params` is True.

    Notes
    -----
    Parameters options can be:

    - A single set of parameters.
      If so, these same parameters are used for all spectra.
    - A list of parameters whose length is n_spectra.
      If so, each successive parameter set is such for each successive spectrum.
    - A generator object that returns parameters for a power spectrum.
      If so, each spectrum has parameters sampled from the generator.

    Aperiodic Parameters:

    - The function for the aperiodic process to use is inferred from the provided parameters.
    - If length of 2, the 'fixed' aperiodic mode is used, if length of 3, 'knee' is used.

    Periodic Parameters:

    - The periodic component is comprised of a set of 'peaks', each of which is described as:

      * Mean (Center Frequency), height (Power), and standard deviation (Bandwidth).
      * Make sure any center frequencies you request are within the simulated frequency range.

    Rotating Power Spectra:

    - You can optionally specify a rotation frequency, such that power spectra will be
      simulated and rotated around that point to the specified aperiodic exponent.

      * This can be used so that any power spectra simulated with the same 'f_rotation'
        will relate to each other by having the specified rotation point.

    - Note that rotating power spectra changes the offset.

      * If you specify an offset value to simulate as well as 'f_rotation', the returned
        spectrum will NOT have the requested offset. It instead will have the offset
        value required to create the requested aperiodic exponent with the requested
        rotation point.
      * If you return SimParams, the recorded offset will be the calculated offset
        of the data post rotation, and not the entered value.

    - You cannot rotate power spectra simulated with a knee.

      * The procedure we use to rotate does not support spectra with a knee, and so
        setting 'f_rotation' with a knee will lead to an error.

    Examples
    --------
    Generate 2 power spectra using the same parameters:

    >>> freqs, powers = sim_group_power_spectra(2, [1, 50], [0, 2], [10, 0.5, 1])

    Generate 10 power spectra, randomly sampling possible parameters:

    >>> from specparam.sim.params import param_sampler
    >>> ap_opts = param_sampler([[0, 1.0], [0, 1.5], [0, 2]])
    >>> pe_opts = param_sampler([[], [10, 0.5, 1], [10, 0.5, 1, 20, 0.25, 1]])
    >>> freqs, powers = sim_group_power_spectra(10, [1, 50], ap_opts, pe_opts)

    Generate 5 power spectra, rotated around 20 Hz:

    >>> ap_params = [[None, 1], [None, 1.25], [None, 1.5], [None, 1.75], [None, 2]]
    >>> pe_params = [10, 0.5, 1]
    >>> freqs, powers = sim_group_power_spectra(5, [1, 50], ap_params, pe_params, f_rotation=20)

    Generate power spectra stepping across exponent values, and return parameter values:

    >>> from specparam.sim.params import Stepper, param_iter
    >>> ap_params = param_iter([0, Stepper(1, 2, 0.25)])
    >>> pe_params = [10, 0.5, 1]
    >>> freqs, powers, sps = sim_group_power_spectra(5, [1, 50], ap_params, pe_params,
    ...                                              return_params=True)
    """

    # Initialize things
    freqs = gen_freqs(freq_range, freq_res)
    powers = np.zeros([n_spectra, len(freqs)])
    sim_params = [None] * n_spectra

    # Check if inputs are generators, if not, make them into repeat generators
    ap_params = check_iter(aperiodic_params, n_spectra)
    pe_params = check_iter(periodic_params, n_spectra)
    nlvs = check_iter(nlvs, n_spectra)
    f_rots = check_iter(f_rotation, n_spectra)

    # Simulate power spectra
    for ind, ap, pe, nlv, f_rot in zip(range(n_spectra), ap_params, pe_params, nlvs, f_rots):

        if f_rotation:
            powers[ind, :] = gen_rotated_power_vals(freqs, ap, check_flat(pe), nlv, f_rot)
            aperiodic_params = [compute_rotation_offset(ap[1], f_rot), ap[1]]

        else:
            powers[ind, :] = gen_power_vals(freqs, ap, check_flat(pe), nlv)

        sim_params[ind] = collect_sim_params(ap, pe, nlv)

    if return_params:
        return freqs, powers, sim_params
    else:
        return freqs, powers


@replace_docstring_sections(\
    docs_replace_param(docs_get_section(\
        sim_group_power_spectra.__doc__, 'Parameters'),
        'n_spectra', 'n_windows : int\n        The number of time windows to generate.'))
def sim_spectrogram(n_windows, freq_range, aperiodic_params, periodic_params,
                    nlvs=0.005, freq_res=0.5, f_rotation=None, return_params=False):
    """Simulate spectrogram.

    Parameters
    ----------
    % copied in from `sim_group_power_spectra`

    Returns
    -------
    freqs : 1d array
        Frequency values, in linear spacing.
    spectrogram : 2d array
        Matrix of power values, in linear spacing, as [n_freqs, n_windows].
    sim_params : list of SimParams
        Definitions of parameters used for each spectrum. Has length of n_spectra.
        Only returned if `return_params` is True.

    Notes
    -----
    This function simulates spectra for the spectrogram using `sim_group_power_spectra`.
    See `sim_group_power_spectra` for details on the parameters.
    """

    outputs = sim_group_power_spectra(n_windows, freq_range, aperiodic_params,
                                      periodic_params, nlvs, freq_res,
                                      f_rotation, return_params)

    outputs = list(outputs)
    outputs[1] = outputs[1].T

    return outputs
