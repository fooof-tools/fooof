"""Utility functions for FOOOF."""

import numpy as np

from fooof.synth import gen_freqs
from fooof.core.utils import get_obj_desc

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
        - It does not round to below or above f_low and f_high, respectively.
    """

    # Create mask to index only requested frequencies
    f_mask = np.logical_and(freqs >= f_range[0], freqs <= f_range[1])

    # Restrict freqs & psd to requested range
    freqs_ext = freqs[f_mask]
    # The if/else is to cover both 1d or 2d arrays
    power_spectra_ext = power_spectra[f_mask] if power_spectra.ndim == 1 \
        else power_spectra[:, f_mask]

    return freqs_ext, power_spectra_ext


def get_settings(f_obj):
    """Get a dictionary of current settings from a FOOOF or FOOOFGroup object.

    Parameters
    ----------
    f_obj : FOOOF or FOOOFGroup
        FOOOF derived object to get settings from.

    Returns
    -------
    dictionary
        Settings for the input FOOOF derived object.
    """

    return {setting : getattr(f_obj, setting) for setting in get_obj_desc()['settings']}


def get_data_info(f_obj):
    """Get a dictionary of current data information from a FOOOF or FOOOFGroup object.

    Parameters
    ----------
    f_obj : FOOOF or FOOOFGroup
        FOOOF derived object to get data information from.

    Returns
    -------
    dictionary
        Data information for the input FOOOF derived object.
    """

    return {dat_info : getattr(f_obj, dat_info) for dat_info in get_obj_desc()['freq_info']}


def compare_settings(lst):
    """Compare the settings between FOOOF and/or FOOOFGroup objects.

    Parameters
    ----------
    lst : list of FOOOF or FOOOFGroup objects
        FOOOF related objects whose settings are to be compared.

    Returns
    -------
    bool
        Whether the settings are consistent across the input list of objects.
    """

    # Check settings are the same across list of given objects
    for ind, f_obj in enumerate(lst[:-1]):
        if get_settings(f_obj) != get_settings(lst[ind+1]):
            return False

    # If no settings fail comparison, return that objects have consistent settings
    return True


def compare_data_info(lst):
    """Compare the data information between FOOOF and/or FOOOFGroup objects.

    Parameters
    ----------
    lst : list of FOOOF or FOOOFGroup objects
        FOOOF related objects whose settings are to be compared.

    Returns
    -------
    bool
        Whether the data information is consistent across the input list of objects.
    """

    # Check data information is the same across the list of given objects
    for ind, f_obj in enumerate(lst[:-1]):
        if get_data_info(f_obj) != get_data_info(lst[ind+1]):
            return False

    # If no data info comparisons fail, return that objects have consistent information
    return True
