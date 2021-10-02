"""Utilities for working with data and models."""

from itertools import repeat

import numpy as np

###################################################################################################
###################################################################################################

def trim_spectrum(freqs, power_spectra, f_range):
    """Extract a frequency range from power spectra.

    Parameters
    ----------
    freqs : 1d array
        Frequency values for the power spectrum.
    power_spectra : 1d or 2d array
        Power spectral density values.
    f_range: list of [float, float]
        Frequency range to restrict to, as [lowest_freq, highest_freq].

    Returns
    -------
    freqs_ext : 1d array
        Extracted frequency values for the power spectrum.
    power_spectra_ext : 1d or 2d array
        Extracted power spectral density values.

    Notes
    -----
    This function extracts frequency ranges >= f_low and <= f_high.
    It does not round to below or above f_low and f_high, respectively.


    Examples
    --------
    Using a simulated spectrum, extract a frequency range:

    >>> from fooof.sim import gen_power_spectrum
    >>> freqs, powers = gen_power_spectrum([1, 50], [1, 1], [10, 0.5, 1.0])
    >>> freqs, powers = trim_spectrum(freqs, powers, [3, 30])
    """

    # Create mask to index only requested frequencies
    f_mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])

    # Restrict freqs & spectra to requested range
    #   The if/else is to cover both 1d or 2d arrays
    freqs_ext = freqs[f_mask]
    power_spectra_ext = power_spectra[f_mask] if power_spectra.ndim == 1 \
        else power_spectra[:, f_mask]

    return freqs_ext, power_spectra_ext


def interpolate_spectrum(freqs, powers, interp_range, buffer=3):
    """Interpolate a frequency region in a power spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency values for the power spectrum.
    powers : 1d array
        Power values for the power spectrum.
    interp_range : list of float or list of list of float
        Frequency range to interpolate, as [lowest_freq, highest_freq].
        If a list of lists, applies each as it's own interpolation range.
    buffer : int or list of int
        The number of samples to use on either side of the interpolation
        range, that are then averaged and used to calculate the interpolation.

    Returns
    -------
    freqs : 1d array
        Frequency values for the power spectrum.
    powers : 1d array
        Power values, with interpolation, for the power spectrum.

    Notes
    -----
    This function takes in, and returns, linearly spaced values.

    This approach interpolates data linearly, in log-log spacing. This assumes a
    1/f property of the data, and so should only be applied where this assumption
    is valid. This approach is intended for interpolating small frequency ranges,
    such as line noise regions.

    The interpolation range is taken as the range from >= interp_range_low and
    <= interp_range_high. It does not round to below or above interp_range_low
    and interp_range_high, respectively.

    To be more robust to noise, this approach takes a number of samples on either
    side of the interpolation range (the number of which is controlled by `buffer`)
    and averages these points to linearly interpolate between them.
    Setting `buffer=1` is equivalent to a linear interpolation between
    the points adjacent to the interpolation range.

    Examples
    --------
    Using a simulated spectrum, interpolate away a line noise peak:

    >>> from fooof.sim import gen_power_spectrum
    >>> freqs, powers = gen_power_spectrum([1, 75], [1, 1], [[10, 0.5, 1.0], [60, 2, 0.1]])
    >>> freqs, powers = interpolate_spectrum(freqs, powers, [58, 62])
    """

    # If given a list of interpolation zones, recurse to apply each one
    if isinstance(interp_range[0], list):
        buffer = repeat(buffer) if isinstance(buffer, int) else buffer
        for interp_zone, cur_buffer in zip(interp_range, buffer):
            freqs, powers = interpolate_spectrum(freqs, powers, interp_zone, cur_buffer)

    # Assuming list of two floats, interpolate a single frequency range
    else:

        # Take a copy of the array, to not change original array
        powers = np.copy(powers)

        # Get the set of frequency values that need to be interpolated
        interp_mask = np.logical_and(freqs >= interp_range[0], freqs <= interp_range[1])
        interp_freqs = freqs[interp_mask]

        # Get the indices of the interpolation range
        ii1, ii2 = np.flatnonzero(interp_mask)[[0, -1]]

        # Extract & log the requested range of data to use around interpolated range
        xs1 = np.log10(freqs[ii1-buffer:ii1])
        xs2 = np.log10(freqs[ii2:ii2+buffer])
        ys1 = np.log10(powers[ii1-buffer:ii1])
        ys2 = np.log10(powers[ii2:ii2+buffer])

        # Linearly interpolate, in log-log space, between averages of the extracted points
        vals = np.interp(np.log10(interp_freqs),
                         [np.median(xs1), np.median(xs2)],
                         [np.median(ys1), np.median(ys2)])
        powers[interp_mask] = np.power(10, vals)

    return freqs, powers


def subsample_spectra(spectra, selection, return_inds=False):
    """Subsample a group of power spectra.

    Parameters
    ----------
    spectra : 2d array
        A group of power spectra to subsample from.
    selection : int or float
        The number of spectra to subsample.
        If int, is the number to select, if float, is a proportion based on input size.
    return_inds : bool, optional, default: False
        Whether to return the list of indices that were selected.

    Returns
    -------
    subsample : 2d array
        A subsampled selection of power spectra.
    inds : list of int
        A list of which indices where subsampled.
        Only returned if `return_inds` is True.

    Examples
    --------
    Using a group of simulated spectra, subsample a specific number:

    >>> from fooof.sim import gen_group_power_spectra
    >>> freqs, powers = gen_group_power_spectra(10, [1, 50], [1, 1], [10, 0.5, 1.0])
    >>> subsample = subsample_spectra(powers, 5)

    Using a group of simulated spectra, subsample a proportion:

    >>> from fooof.sim import gen_group_power_spectra
    >>> freqs, powers = gen_group_power_spectra(10, [1, 50], [1, 1], [10, 0.5, 1.0])
    >>> subsample = subsample_spectra(powers, 0.25)
    """

    n_spectra = spectra.shape[0]

    if isinstance(selection, float):
        n_sample = int(n_spectra * selection)
    else:
        n_sample = selection

    inds = np.random.choice(n_spectra, n_sample, replace=False)
    subsample = spectra[inds, :]

    if return_inds:
        return subsample, inds
    else:
        return subsample
