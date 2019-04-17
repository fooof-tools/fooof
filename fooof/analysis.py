"""Analysis functions for FOOOF results."""

import numpy as np

###################################################################################################
###################################################################################################

def get_band_peak_fm(fm, band, ret_one=True, attribute='peak_params'):
    """Extract peaks from a band of interest from a FOOOFGroup object.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object to extract peak data from.
    band : tuple of (float, float)
        Defines the band of interest, as (lower_frequency_bound, upper_frequency_bound).
    ret_one : bool, optional, default: True
        Whether to return single peak (if True) or all peaks within the range found (if False).
        If True, returns the highest power peak within the search range.
    attribute : {'peak_params', 'gaussian_params'}
        Which attribute of peak data to extract data from.

    Returns
    -------
    1d or 2d array
        Peak data. Each row is a peak, as [CF, Amp, BW]
    """

    return get_band_peak(getattr(fm, attribute + '_'), band, ret_one)


def get_band_peak_fg(fg, band, attribute='peak_params'):
    """Extract peaks from a band of interest from a FOOOF object.

    Parameters
    ----------
    fg : FOOOFGroup
        FOOOFGroup object to extract peak data from.
    band : tuple of (float, float)
        Defines the band of interest, as (lower_frequency_bound, upper_frequency_bound).
    attribute : {'peak_params', 'gaussian_params'}
        Which attribute of peak data to extract data from.

    Returns
    -------
    2d array
        Peak data. Each row is a peak, as [CF, Amp, BW].
    """

    return get_band_peak_group(fg.get_params(attribute), band, len(fg))


def get_band_peak_group(peak_params, band, n_fits):
    """Extracts peaks within a given band of interest.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, for a group fit, from FOOOF, with shape of [n_peaks, 4].
    band : tuple of (float, float)
        Defines the band of interest, as (lower_frequency_bound, upper_frequency_bound).
    n_fits : int
        The number of model fits in the FOOOFGroup data.

    Returns
    -------
    band_peaks : 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].

    Notes
    -----
    This function conserves the shape of the array, returning a [n_fits, 3] array.

    * Each row reflects a FOOOF model fit, in order, filled with NaN if no peak was present.

    * To do so, this function necessarily extracts and returns one peak per model fit.

    If, instead, you with to extract all peaks within a band, per model fit, you can do:

    >>> peaks = np.empty((0, 3))
    >>> for f_res in fg:
    >>>     peaks = np.vstack((peaks, get_band_peak(f_res.peak_params, band, ret_one=False)))

    """

    band_peaks = np.zeros(shape=[n_fits, 3])

    # Extacts an array per FOOOF fit, and extracts band peaks from it
    for ind in range(n_fits):
        band_peaks[ind, :] = get_band_peak(peak_params[tuple([peak_params[:, -1] == ind])][:, 0:3],
                                           band=band, ret_one=True)

    return band_peaks


def get_band_peak(peak_params, band, ret_one=True):
    """Extracts peaks within a given band of interest.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, from FOOOF, with shape of [n_peaks, 3].
    band : tuple of (float, float)
        Defines the band of interest, as (lower_frequency_bound, upper_frequency_bound).
    ret_one : bool, optional, default: True
        Whether to return single peak (if True) or all peaks within the range found (if False).
        If True, returns the highest peak within the search range.

    Returns
    -------
    band_peaks : 1d or 2d array
        Peak data. Each row is a peak, as [CF, PW, BW]
    """

    # Return nan array if empty input
    if peak_params.size == 0:
        return np.array([np.nan, np.nan, np.nan])

    # Find indices of peaks in the specified range, and check the number found
    peak_inds = (peak_params[:, 0] >= band[0]) & (peak_params[:, 0] <= band[1])
    n_peaks = sum(peak_inds)

    # If there are no peaks within the specified range
    #  Note: this also catches and returns if the original input was empty
    if n_peaks == 0:
        return np.array([np.nan, np.nan, np.nan])

    band_peaks = peak_params[peak_inds, :]

    # If results > 1 and ret_one, then we return the highest peak
    #    Call a sub-function to select highest power peak in band
    if n_peaks > 1 and ret_one:
        band_peaks = get_highest_peak(band_peaks)

    # If results == 1, return single peak
    return np.squeeze(band_peaks)


def get_highest_peak(band_peaks):
    """Searches for the highest peak.

    Parameters
    ----------
    band_peaks : 2d array
        Peak parameters, from FOOOF, with shape of [n_peaks, 3].

    Returns
    -------
    1d array
        Peak data. Each row is a peak, as [CF, PW, BW].
    """

    # Catch & return NaN if empty
    if len(band_peaks) == 0:
        return np.array([np.nan, np.nan, np.nan])

    high_ind = np.argmax(band_peaks[:, 1])

    return band_peaks[high_ind, :]
