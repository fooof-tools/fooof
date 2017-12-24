"""Basic analysis functions for FOOOF results."""

import numpy as np

###################################################################################################
###################################################################################################

def get_band_peak(peak_params, band_def, ret_one=True):
    """Searches for peaks within a given band of interest.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, from FOOOF. [n_peaks, 3]
    band_def : [float, float]
        Defines the band of interest.
    ret_one : bool
        Whether to return single peak (or all found).

    Return
    ---------
    band_peaks : array
        Peak data, form - (centers, powers, bws).
    """

    # Find indices of peaks in the specified range
    peak_inds = (peak_params[:, 0] >= band_def[0]) & (peak_params[:, 0] <= band_def[1])

    # Gets the number of peaks within the specified range
    n_peaks = sum(peak_inds)

    # If there are no peaks within the specified range
    #  Note: this also catches and returns if the original input was empty
    if n_peaks == 0:
        return np.array([np.nan, np.nan, np.nan])

    band_peaks = peak_params[peak_inds, :]

    # If results > 1 and ret_one, then we return the highest amplitude peak
    #    Call a sub-function to select highest power peak
    if n_peaks > 1 and ret_one:
        # Get highest amplitude peak in band
        band_peaks = get_highest_amp_peak(band_peaks)

    # If results == 1, return peak - [cen, power, bw]
    return np.squeeze(band_peaks)


def get_highest_amp_peak(band_peaks):
    """Searches for the highest amplitude peak.

    Parameters
    ----------
    peak_params : 2d array
        Peak parameters, from FOOOF. [n_peaks, 3]

    Return
    ---------
    band_peaks : array
        Peak parameters, form - (centers, powers, bws).
    """

    # Catch & return if empty
    if len(band_peaks) == 0:
        return np.array([np.nan, np.nan, np.nan])

    high_ind = np.argmax(band_peaks[:, 1])

    return band_peaks[high_ind, :]
