"""Basic analysis functions for FOOOF results."""

import numpy as np

###################################################################################################
###################################################################################################

def get_band_peak_group(peak_params, band_def, n_fits):
    """Extracts peaks within a given band of interest, for a group of FOOOF model fits.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, for a group fit, from FOOOF. [n_peaks, 4]
    band_def : [float, float]
        Defines the band of interest.
    n_fits : int
        The number of model fits in the FOOOFGroup data.

    Returns
    -------
    band_peaks : 2d array
        Peak data. Each row is a peak, as [CF, Amp, BW].

    Notes
    -----
    - This function conserves the shape of the array, return a [n_fits, 3] array.
      - Each row reflects a FOOOF model fit, in order, filled with NaN if no peak was present.
    - To do so, this function necessarily extracts and returns one peak per model fit.
    - For extracting all peaks within a band, per model fit, you can do:
    $ peaks = np.empty((0, 3))
    $ for f_res in fg:
    $     peaks = np.vstack((peaks, get_band_peak(f_res.peak_params, band_def, ret_one=False)))
    """

    band_peaks = np.zeros(shape=[n_fits, 3])
    for ind in range(n_fits):

        # Extacts an array per FOOOF fit, and extracts band peaks from it
        band_peaks[ind, :] = get_band_peak(peak_params[[peak_params[:, -1] == ind]][:, 0:3],
                                           band_def=band_def, ret_one=True)

    return band_peaks


def get_band_peak(peak_params, band_def, ret_one=True):
    """Extracts peaks within a given band of interest, for a FOOOF model fit.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, from FOOOF. [n_peaks, 3]
    band_def : [float, float]
        Defines the band of interest.
    ret_one : bool
        Whether to return single peak (or all found).
            If True, returns the highest amplitude peak.

    Returns
    -------
    band_peaks : 1d or 2d array
        Peak data. Each row is a peak, as [CF, Amp, BW].
    """

    # Return nan array if empty input
    if peak_params.size == 0:
        return np.array([np.nan, np.nan, np.nan])

    # Find indices of peaks in the specified range, and check the number found
    peak_inds = (peak_params[:, 0] >= band_def[0]) & (peak_params[:, 0] <= band_def[1])
    n_peaks = sum(peak_inds)

    # If there are no peaks within the specified range
    #  Note: this also catches and returns if the original input was empty
    if n_peaks == 0:
        return np.array([np.nan, np.nan, np.nan])

    band_peaks = peak_params[peak_inds, :]

    # If results > 1 and ret_one, then we return the highest amplitude peak
    #    Call a sub-function to select highest power peak in band
    if n_peaks > 1 and ret_one:
        band_peaks = get_highest_amp_peak(band_peaks)

    # If results == 1, return peak - [cen, power, bw]
    return np.squeeze(band_peaks)


def get_highest_amp_peak(band_peaks):
    """Searches for the highest amplitude peak.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, from FOOOF. [n_peaks, 3]

    Returns
    -------
    band_peaks : array
        Peak parameters, form - (centers, powers, bws).
    """

    # Catch & return if empty
    if len(band_peaks) == 0:
        return np.array([np.nan, np.nan, np.nan])

    high_ind = np.argmax(band_peaks[:, 1])

    return band_peaks[high_ind, :]
