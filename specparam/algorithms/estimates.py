"""Estimate properties from data."""

import numpy as np

###################################################################################################
###################################################################################################

def estimate_fwhm(flatspec, peak_ind, freq_res):
    """Estimate the Full-Width Half Max (FWHM) given a peak index for a flattened power spectrum.

    Parameters
    ----------
    flatspec : 1d array
        Flattened power spectrum.
    peak_ind : int
        Index of the peak in the flattened spectrum to compute FWHM for.
    freq_res : float
        Frequency resolution.

    Returns
    -------
    fwhm : float
        Estimated full width half maximum of a peak.
        This can be NaN if the FWHM could not be estimated.

    Notes
    -----
    Though FWHM are in theory symmetric (for a Gaussian), this procedure estimates the FWHM from
    the shortest side of the peak. This is to deal with potential cases of overlapping peaks that
    can elongate one side in a way that would bias the FWHM estimate to be greater than desired.
    """

    # Find half height index on each side of the given peak index
    half_height = 0.5 * flatspec[peak_ind]
    le_ind = next((val for val in range(peak_ind - 1, 0, -1) \
                  if flatspec[val] <= half_height), None)
    ri_ind = next((val for val in range(peak_ind + 1, len(flatspec), 1) \
                  if flatspec[val] <= half_height), None)

    try:
        # Get estimated width from the shortest side, ignoring a side if the half max was not found
        short_side = min([abs(ind - peak_ind) \
            for ind in [le_ind, ri_ind] if ind is not None])

        # Use short side to estimate FWHM, also converting estimate to Hz
        fwhm = short_side * 2 * freq_res

    except ValueError:
        # This process can fail if both sides end up as none - in which case, return as nan
        fwhm = np.nan

    return fwhm
