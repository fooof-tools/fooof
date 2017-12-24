"""Utility functions for FOOOF."""

import numpy as np

###################################################################################################
###################################################################################################

def trim_psd(freqs, psd, f_range):
    """Extract frequency range of interest from PSD data.

    Parameters
    ----------
    freqs : 1d array
        Frequency values for the PSD.
    psd : 1d or 2d array
        Power spectral density values.
    f_range: list of [float, float]
        Frequency range to restrict to.

    Returns
    -------
    freqs_ext : 1d array
        Extracted power spectral density values.
    psd_ext : 1d array
        Extracted frequency values for the PSD.

    Notes
    -----
    This function extracts frequency ranges >= f_low and <= f_high.
        - It does not round to below or above f_low and f_high, respectively.
    """

    # Create mask to index only requested frequencies
    f_mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])

    # Restrict freqs & psd to requested range
    freqs_ext = freqs[f_mask]
    psd_ext = psd[f_mask] if psd.ndim == 1 else psd[:, f_mask]

    return freqs_ext, psd_ext
