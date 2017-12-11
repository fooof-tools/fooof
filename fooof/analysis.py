"""Basic oscillation analysis functions for FOOOF."""

import numpy as np

###################################################################################################
###################################################################################################

def get_band_osc(osc_params, band_def, ret_one=True):
    """Searches for oscillations within a given band of interest.

    Parameters
    ----------
    osc_params : 2d array
        Oscillations parameters, from FOOOF. [n_oscs, 3]
    band_def : [float, float]
        Defines the band of interest
    ret_one : bool
        Whether to return single oscillation (or all found)

    Return
    ---------
    band_oscs : array
        Osc data, form - (centers, powers, bws.
    """

    # Find indices of oscillations in the specified range
    osc_inds = (osc_params[:, 0] >= band_def[0]) & (osc_params[:, 0] <= band_def[1])

    # Gets the number of oscillations within the specified range
    n_oscs = sum(osc_inds)

    # If there are no oscillation within the specified range
    #  Note: this also catches and returns if the original input was empty
    if n_oscs == 0:
        return np.array([np.nan, np.nan, np.nan])

    band_oscs = osc_params[osc_inds, :]

    # If results > 1 and ret_one, then we return the highest power oscillation
    #    Call a sub-function to select highest power oscillation
    if n_oscs > 1 and ret_one:
        # Get highest power oscillation in band
        band_oscs = get_highest_power_osc(band_oscs)

    # If results == 1, return osc - [cen, power, bw]
    return np.squeeze(band_oscs)


def get_highest_power_osc(band_oscs):
    """Searches for the highest power oscillation.

    Parameters
    ----------
    osc_params : 2d array
        Oscillations parameters, from FOOOF. [n_oscs, 3]

    Return
    ---------
    band_oscs : array
        Osc data, form - (centers, powers, bws).
    """

    # Catch & return if empty
    if len(band_oscs) == 0:
        return np.array([np.nan, np.nan, np.nan])

    high_ind = np.argmax(band_oscs[:, 1])
    return band_oscs[high_ind, :]
