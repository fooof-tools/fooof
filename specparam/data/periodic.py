"""Functions to analyze and investigate model fit results - periodic components."""

import numpy as np

###################################################################################################
###################################################################################################

def get_band_peak(model, band, select_highest=True, threshold=None,
                  thresh_param='PW', attribute='peak_params'):
    """Extract peaks from a band of interest from a model object.

    Parameters
    ----------
    model : SpectralModel
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
    peaks : 1d or 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].

    Examples
    --------
    Select an alpha peak from a fit model object 'model', selecting the highest power alpha:

    >>> alpha = get_band_peak(model, [7, 14], select_highest=True)  # doctest:+SKIP

    Select beta peaks from a model object 'model', extracting all peaks in the range:

    >>> betas = get_band_peak(model, [13, 30], select_highest=False)  # doctest:+SKIP
    """

    return get_band_peak_arr(getattr(model.results, attribute + '_'), band,
                             select_highest, threshold, thresh_param)


def get_band_peak_group(group, band, threshold=None, thresh_param='PW', attribute='peak_params'):
    """Extract peaks from a band of interest from a group model object.

    Parameters
    ----------
    group : SpectralGroupModel
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
    peaks : 2d array
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
    >>> for res in group:  # doctest:+SKIP
    ...     peaks = np.vstack((peaks, get_band_peak(res.peak_params, band, select_highest=False)))

    Examples
    --------
    Extract alpha peaks from a group model object 'group' that already has model results:

    >>> alphas = get_band_peak_group(group, [7, 14])  # doctest:+SKIP

    Extract peaks from a group model object 'group', selecting those above a power threshold:

    >>> betas = get_band_peak_group(group, [13, 30], threshold=0.1)  # doctest:+SKIP
    """

    return get_band_peak_group_arr(group.results.get_params(attribute), band, len(group.results),
                                   threshold, thresh_param)


def get_band_peak_event(event, band, threshold=None, thresh_param='PW', attribute='peak_params'):
    """Extract peaks from a band of interest from an event model object.

    Parameters
    ----------
    event : SpectralTimeEventModel
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
    peaks : 3d array
        Array of peak data, organized as [n_events, n_time_windows, n_peak_params].
    """

    peaks = np.zeros([event.data.n_events, event.data.n_time_windows, 3])
    for ind in range(event.data.n_events):
        peaks[ind, :, :] = get_band_peak_group(\
            event.get_group(ind, None, 'group'), band, threshold, thresh_param, attribute)

    return peaks


def get_band_peak_group_arr(peak_params, band, n_fits, threshold=None, thresh_param='PW'):
    """Extract peaks within a given band of interest, from peaks from a group fit.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, for a group fit, with shape of [n_peaks, 4].
    band : tuple of (float, float)
        Frequency range for the band of interest.
        Defined as: (lower_frequency_bound, upper_frequency_bound).
    n_fits : int
        The number of model fits in the group.
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

    # Extracts an array per model fit, and extracts band peaks from it
    band_peaks = np.zeros(shape=[n_fits, 3])
    for ind in range(n_fits):
        band_peaks[ind, :] = get_band_peak_arr(\
            peak_params[tuple([peak_params[:, -1] == ind])][:, 0:3],
            band=band, select_highest=True, threshold=threshold, thresh_param=thresh_param)

    return band_peaks


def get_band_peak_arr(peak_params, band, select_highest=True, threshold=None, thresh_param='PW'):
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
    #   TEMP: interim hardcode for parameter index while updating for modes
    thresh_mask = peak_params[:, {'PW' : 1, 'BW' : 2}[param]] > threshold
    thresholded_peaks = peak_params[thresh_mask]

    return thresholded_peaks
