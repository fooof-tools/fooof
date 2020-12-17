"""Functions to analyze and investigate FOOOF results - periodic components."""

import numpy as np

from fooof.core.items import PEAK_INDS

###################################################################################################
###################################################################################################

def get_band_peak_fm(fm, band, select_highest=True, threshold=None, thresh_param='PW',
                     attribute='peak_params',):
    """Extract peaks from a band of interest from a FOOOF object.

    Parameters
    ----------
    fm : FOOOF
        Object to extract peak data from.
    band : tuple of (float, float)
        Frequency range for the band of interest.
        Defined as: (lower_frequency_bound, upper_frequency_bound).
    select_highest : bool, optional, default: True
        Whether to return single peak (if True) or all peaks within the range found (if False).
        If True, returns the highest power peak within the search range.
    threshold : float, optional
        A minimum threshold value to apply.
    thresh_param : {'PW', 'BW'}
        Which parameter to threshold on. 'PW' is power and 'BW' is bandwidth.
    attribute : {'peak_params', 'gaussian_params'}
        Which attribute of peak data to extract data from.

    Returns
    -------
    1d or 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].

    Examples
    --------
    Select an alpha peak from an already fit FOOOF object 'fm', selecting the highest power alpha:

    >>> alpha = get_band_peak_fm(fm, [7, 14], select_highest=True)  # doctest:+SKIP

    Select beta peaks from a FOOOF object 'fm', extracting all peaks in the range:

    >>> betas = get_band_peak_fm(fm, [13, 30], select_highest=False)  # doctest:+SKIP
    """

    return get_band_peak(getattr(fm, attribute + '_'), band,
                         select_highest, threshold, thresh_param)


def get_band_peak_fg(fg, band, threshold=None, thresh_param='PW', attribute='peak_params'):
    """Extract peaks from a band of interest from a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to extract peak data from.
    band : tuple of (float, float)
        Frequency range for the band of interest.
        Defined as: (lower_frequency_bound, upper_frequency_bound).
    threshold : float, optional
        A minimum threshold value to apply.
    thresh_param : {'PW', 'BW'}
        Which parameter to threshold on. 'PW' is power and 'BW' is bandwidth.
    attribute : {'peak_params', 'gaussian_params'}
        Which attribute of peak data to extract data from.

    Returns
    -------
    2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
        Each row represents an individual model from the input object.

    Notes
    -----
    The returned array keeps track of which model each extracted peak comes from,
    returning a [n_models, 3] array, with one peak returned per model.

    - To do so, this function necessarily extracts and returns one peak per model fit.
    - Each row reflects an individual model fit, in order, filled with nan if no peak was present.

    If, instead, you wish to extract all peaks within a band, per model fit,
    you can do something like:

    >>> peaks = np.empty((0, 3))
    >>> for f_res in fg:  # doctest:+SKIP
    ...     peaks = np.vstack((peaks, get_band_peak(f_res.peak_params, band, select_highest=False)))

    Examples
    --------
    Extract alpha peaks from a FOOOFGroup object 'fg' that already has model results:

    >>> alphas = get_band_peak_fg(fg, [7, 14])  # doctest:+SKIP

    Extract peaks from a FOOOFGroup object 'fg', selecting those above a power threshold:

    >>> betas = get_band_peak_fg(fg, [13, 30], threshold=0.1)  # doctest:+SKIP
    """

    return get_band_peak_group(fg.get_params(attribute), band, len(fg),
                               threshold, thresh_param)


def get_band_peak_group(peak_params, band, n_fits, threshold=None, thresh_param='PW'):
    """Extract peaks within a given band of interest, from peaks from a group fit.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, for a group fit, with shape of [n_peaks, 4].
    band : tuple of (float, float)
        Frequency range for the band of interest.
        Defined as: (lower_frequency_bound, upper_frequency_bound).
    n_fits : int
        The number of model fits in the FOOOFGroup data.
    threshold : float, optional
        A minimum threshold value to apply.
    thresh_param : {'PW', 'BW'}
        Which parameter to threshold on. 'PW' is power and 'BW' is bandwidth.

    Returns
    -------
    band_peaks : 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
        Each row represents an individual model from the input array of all peaks.

    Notes
    -----
    The returned array keeps track of which model each extracted peak comes from,
    returning a [n_models, 3] array, with one peak returned per model.

    - To do so, this function necessarily extracts and returns one peak per model fit.
    - Each row reflects an individual model fit, in order, filled with nan if no peak was present.
    """

    # Extracts an array per FOOOF fit, and extracts band peaks from it
    band_peaks = np.zeros(shape=[n_fits, 3])
    for ind in range(n_fits):
        band_peaks[ind, :] = get_band_peak(peak_params[tuple([peak_params[:, -1] == ind])][:, 0:3],
                                           band=band, select_highest=True,
                                           threshold=threshold,
                                           thresh_param=thresh_param)

    return band_peaks


def get_band_peak(peak_params, band, select_highest=True, threshold=None, thresh_param='PW'):
    """Extract peaks within a given band of interest.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, with shape of [n_peaks, 3].
    band : tuple of (float, float)
        Frequency range for the band of interest.
        Defined as: (lower_frequency_bound, upper_frequency_bound).
    select_highest : bool, optional, default: True
        Whether to return single peak (if True) or all peaks within the range found (if False).
        If True, returns the highest peak within the search range.
    threshold : float, optional
        A minimum threshold value to apply.
    thresh_param : {'PW', 'BW'}
        Which parameter to threshold on. 'PW' is power and 'BW' is bandwidth.

    Returns
    -------
    band_peaks : 1d or 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
    """

    # Return nan array if empty input
    if peak_params.size == 0:
        return np.array([np.nan, np.nan, np.nan])

    # Find indices of peaks in the specified range, and check the number found
    peak_inds = (peak_params[:, 0] >= band[0]) & (peak_params[:, 0] <= band[1])
    n_peaks = sum(peak_inds)

    # If there are no peaks within the specified range, return nan
    #   Note: this also catches and returns if the original input was empty
    if n_peaks == 0:
        return np.array([np.nan, np.nan, np.nan])

    band_peaks = peak_params[peak_inds, :]

    # Apply a minimum threshold, if one was provided
    if threshold:
        band_peaks = threshold_peaks(band_peaks, threshold, thresh_param)

    # If results > 1 and select_highest, then we return the highest peak
    #    Call a sub-function to select highest power peak in band
    if n_peaks > 1 and select_highest:
        band_peaks = get_highest_peak(band_peaks)

    # Squeeze so that if there is only 1 result, return single peak in flat array
    return np.squeeze(band_peaks)


def get_highest_peak(peak_params):
    """Extract the highest power peak.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, with shape of [n_peaks, 3].

    Returns
    -------
    1d array
        Peak data. The row is a peak, as [CF, PW, BW].

    Notes
    -----
    This function returns the singular highest power peak from the input set, and as
    such is defined to work on periodic parameters from a single model fit.
    """

    # Catch & return NaN if empty
    if len(peak_params) == 0:
        return np.array([np.nan, np.nan, np.nan])

    high_ind = np.argmax(peak_params[:, 1])

    return peak_params[high_ind, :]


def threshold_peaks(peak_params, threshold, param='PW'):
    """Extract peaks that are above a given threshold value.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, with shape of [n_peaks, 3] or [n_peaks, 4].
    threshold : float
        A minimum threshold value to apply.
    param : {'PW', 'BW'}
        Which parameter to threshold on. 'PW' is power and 'BW' is bandwidth.

    Returns
    -------
    thresholded_peaks : 2d array
        Peak parameters, with shape of [n_peaks, :].

    Notes
    -----
    This function can be applied to periodic parameters from an individual model,
    or a set or parameters from a group.
    """

    # Catch if input is empty & return nan if so
    if len(peak_params) == 0:
        return np.array([np.nan, np.nan, np.nan])

    # Otherwise, apply a mask to apply the requested threshold
    thresh_mask = peak_params[:, PEAK_INDS[param]] > threshold
    thresholded_peaks = peak_params[thresh_mask]

    return thresholded_peaks
