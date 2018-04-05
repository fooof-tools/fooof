"""Utility functions for FOOOF.

Notes
-----
- FOOOFGroup is imported directly in the functions that require it.
    - This is to avoid a broken import circularity otherwise.
"""

import numpy as np

from fooof.core.modutils import get_obj_desc

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
        Extracted power spectral density values.
    power_spectra_ext : 1d array
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

    # Runs through all settings, and
    for setting in get_obj_desc()['settings']:
        for ind, f_obj in enumerate(lst[:-1]):

            # If any setting fails comparison, return that objects are incompatible
            if getattr(f_obj, setting) != getattr(lst[ind+1], setting):
                return False

    # If no settings fail comparison, return that objects have consistent settings
    return True


def combine_fooofs(fooofs):
    """Combine a group of FOOOF objects into a single FOOOFGroup object.

    Parameters
    ----------
    fooofs : list of FOOOF objects
        FOOOF objects to be concatenated into a FOOOFGroup.

    Returns
    -------
    fg : FOOOFGroup object
        Resultant FOOOFGroup object created from input FOOOFs.
    """

    # Compare settings
    if not compare_settings(fooofs):
        raise ValueError('These objects have incompatible settings, and so cannot be combined.')

    # Initialize FOOOFGroup object, with settings derived from input objects
    from fooof import FOOOFGroup
    fg = FOOOFGroup(**get_settings(fooofs[0]), verbose=fooofs[0].verbose)

    # Add FOOOF results from each FOOOF object to group
    for fm in fooofs:
        fg.group_results.append(fm.get_results())

    return fg


def combine_fooof_groups(fooof_groups):
    """Combine a group of FOOOFGroup objects into a new combined FOOOFGroup object.

    Parameters
    ----------
    fooof_groups : list of FOOOFGroup objects
        FOOOFGroup objectst to be concatenated into a single new FOOOFGroup object.

    Returns
    -------
    fg : FOOOFGroup object
        New FOOOFGroup object built from input FOOOFGroups.
    """

    # Compare settings
    if not compare_settings(fooof_groups):
        raise ValueError('These objects have incompatible settings, and so cannot be combined.')

    # Initialize FOOOFGroup object, with settings derived from input objects
    from fooof import FOOOFGroup
    fg = FOOOFGroup(**get_settings(fooof_groups[0]), verbose=fooof_groups[0].verbose)

    # Add FOOOF results from each FOOOF object to group
    for tfg in fooof_groups:
        fg.group_results.extend(tfg.group_results)

    return fg
