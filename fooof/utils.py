"""Public utility & helper functions for FOOOF."""

import numpy as np

from fooof.core.info import get_description

###################################################################################################
###################################################################################################

def trim_spectrum(freqs, power_spectra, f_range):
    """Extract frequency range of interest from power spectra.

    Parameters
    ----------
    freqs : 1d array
        Frequency values for the PSD.
    power_spectra : 1d or 2d array
        Power spectral density values.
    f_range: list of [float, float]
        Frequency range to restrict to.

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
    """

    # Create mask to index only requested frequencies
    f_mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])

    # Restrict freqs & psd to requested range. The if/else is to cover both 1d or 2d arrays
    freqs_ext = freqs[f_mask]
    power_spectra_ext = power_spectra[f_mask] if power_spectra.ndim == 1 \
        else power_spectra[:, f_mask]

    return freqs_ext, power_spectra_ext


def get_info(f_obj, aspect):
    """Get a specified selection of information from a FOOOF derived object.

    Parameters
    ----------
    f_obj : FOOOF or FOOOFGroup
        FOOOF derived object to get attributes from.
    aspect : {'settings', 'meta_data', 'results'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    dict
        The set of specified info from the FOOOF derived object.
    """

    return {key : getattr(f_obj, key) for key in get_description()[aspect]}


def compare_info(lst, aspect):
    """Compare a specified aspect of FOOOF objects across instances.

    Parameters
    ----------
    lst : list of FOOOF or FOOOFGroup objects
        FOOOF related objects whose attibutes are to be compared.
    aspect : {'setting', 'meta_data'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    consistent : bool
        Whether the settings are consistent across the input list of objects.
    """

    # Check specified aspect of the objects are the same across instances
    for f_obj_1, f_obj_2 in zip(lst[:-1], lst[1:]):
        if getattr(f_obj_1, 'get_' + aspect)() != getattr(f_obj_2, 'get_' + aspect)():
            consistent = False
            break
    else:
        consistent = True

    return consistent
