"""Helper functions for running and working with FOOOF & FOOOFGroup objects."""

import numpy as np

from fooof import FOOOF, FOOOFGroup
from fooof.data import FOOOFResults
from fooof.utils import compare_info
from fooof.analysis import get_band_peak_fg

###################################################################################################
###################################################################################################

def average_fg(fg, bands, avg_method='mean'):
    """Average across a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup
        A FOOOFGroup object with data to average across.
    bands : Bands
        Bands object that defines the frequency bands to collapse peaks across.
    avg : {'mean', 'median'}
        Averaging function to use.

    Returns
    -------
    fm : FOOOF
        FOOOF object containing the average results from the FOOOFGroup input.
    """

    if avg_method not in ['mean', 'median']:
        raise ValueError('Requested average method not understood.')
    if not len(fg):
        raise ValueError('Input FOOOFGroup has no fit results - can not proceed.')

    if avg_method == 'mean':
        avg_func = np.nanmean
    elif avg_method == 'median':
        avg_func = np.nanmedian

    ap_params = avg_func(fg.get_params('aperiodic_params'), 0)

    peak_params = np.array([avg_func(get_band_peak_fg(fg, band, 'peak_params'), 0) \
                            for label, band in bands])
    gaussian_params = np.array([avg_func(get_band_peak_fg(fg, band, 'gaussian_params'), 0) \
                                for label, band in bands])

    r2 = avg_func(fg.get_params('r_squared'))
    error = avg_func(fg.get_params('error'))

    results = FOOOFResults(ap_params, peak_params, r2, error, gaussian_params)

    # Create the new FOOOF object, with settings, data info & results
    fm = FOOOF()
    fm.add_settings(fg.get_settings())
    fm.add_meta_data(fg.get_meta_data())
    fm.add_results(results)

    return fm


def combine_fooofs(fooofs):
    """Combine a group of FOOOF and/or FOOOFGroup objects into a single FOOOFGroup object.

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
    if not compare_info(fooofs, 'settings') or not compare_info(fooofs, 'meta_data'):
        raise ValueError("These objects have incompatible settings or meta data," \
                         "and so cannot be combined.")

    # Initialize FOOOFGroup object, with settings derived from input objects
    fg = FOOOFGroup(*fooofs[0].get_settings(), verbose=fooofs[0].verbose)

    # Use a temporary store to collect spectra, because we only add them if consistently present
    temp_power_spectra = np.empty([0, len(fooofs[0].freqs)])

    # Add FOOOF results from each FOOOF object to group
    for f_obj in fooofs:
        # Add FOOOFGroup object
        if isinstance(f_obj, FOOOFGroup):
            fg.group_results.extend(f_obj.group_results)
            if f_obj.power_spectra is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, f_obj.power_spectra])
        # Add FOOOF object
        else:
            fg.group_results.append(f_obj.get_results())
            if f_obj.power_spectrum is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, f_obj.power_spectrum])

    # If the number of collected power spectra is consistent, then add them to object
    if len(fg) == temp_power_spectra.shape[0]:
        fg.power_spectra = temp_power_spectra

    # Add data information information
    fg.add_meta_data(fooofs[0].get_meta_data())

    return fg


def fit_fooof_group_3d(fg, freqs, power_spectra, freq_range=None, n_jobs=1):
    """Run FOOOFGroup across a 3D collection of power spectra.

    Parameters
    ----------
    fg : FOOOFGroup
        Fitting object, pre-initialized with desired settings, to fit with.
    freqs : 1d array
        Frequency values for the power spectra, in linear space.
    power_spectra : 3d array
        Power values, in linear space, as [n_conditions, n_power_spectra, n_freqs].
    freq_range : list of [float, float], optional
        Desired frequency range to fit. If not provided, fits the entire given range.
    n_jobs : int, optional, default: 1
        Number of jobs to run in parallel.
        1 is no parallelization. -1 uses all available cores.

    Returns
    -------
    fgs : list of FOOOFGroups
        Collected FOOOFGroups after fitting across power spectra, length of n_conditions.
    """

    fgs = []
    for cond_spectra in power_spectra:
        fg.fit(freqs, cond_spectra, freq_range, n_jobs)
        fgs.append(fg.copy())

    return fgs
