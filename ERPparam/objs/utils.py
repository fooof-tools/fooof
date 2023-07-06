"""Utility functions for managing and manipulating ERPparam objects."""

import numpy as np

from ERPparam.sim import gen_freqs
from ERPparam.data import ERPparamResults
from ERPparam.objs import ERPparam, ERPparamGroup
from ERPparam.analysis.periodic import get_band_peak_fg
from ERPparam.core.errors import NoModelError, IncompatibleSettingsError

###################################################################################################
###################################################################################################

def compare_info(ERPparam_lst, aspect):
    """Compare a specified aspect of ERPparam objects across instances.

    Parameters
    ----------
    ERPparam_lst : list of ERPparam and / or ERPparamGroup
        Objects whose attributes are to be compared.
    aspect : {'settings', 'meta_data'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    consistent : bool
        Whether the settings are consistent across the input list of objects.
    """

    # Check specified aspect of the objects are the same across instances
    for f_obj_1, f_obj_2 in zip(ERPparam_lst[:-1], ERPparam_lst[1:]):
        if getattr(f_obj_1, 'get_' + aspect)() != getattr(f_obj_2, 'get_' + aspect)():
            consistent = False
            break
    else:
        consistent = True

    return consistent


def average_fg(fg, bands, avg_method='mean', regenerate=True):
    """Average across model fits in a ERPparamGroup object.

    Parameters
    ----------
    fg : ERPparamGroup
        Object with model fit results to average across.
    bands : Bands
        Bands object that defines the frequency bands to collapse peaks across.
    avg : {'mean', 'median'}
        Averaging function to use.
    regenerate : bool, optional, default: True
        Whether to regenerate the model for the averaged parameters.

    Returns
    -------
    fm : ERPparam
        Object containing the average model results.

    Raises
    ------
    ValueError
        If the requested averaging method is not understood.
    NoModelError
        If there are no model fit results available to average across.
    """

    if avg_method not in ['mean', 'median']:
        raise ValueError("Requested average method not understood.")
    if not fg.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    if avg_method == 'mean':
        avg_func = np.nanmean
    elif avg_method == 'median':
        avg_func = np.nanmedian

    # Aperiodic parameters: extract & average
    ap_params = avg_func(fg.get_params('aperiodic_params'), 0)

    # Periodic parameters: extract & average
    peak_params = []
    gauss_params = []

    for band_def in bands.definitions:

        peaks = get_band_peak_fg(fg, band_def, attribute='peak_params')
        gauss = get_band_peak_fg(fg, band_def, attribute='gaussian_params')

        # Check if there are any extracted peaks - if not, don't add
        #   Note that we only check peaks, but gauss should be the same
        if not np.all(np.isnan(peaks)):
            peak_params.append(avg_func(peaks, 0))
            gauss_params.append(avg_func(gauss, 0))

    peak_params = np.array(peak_params)
    gauss_params = np.array(gauss_params)

    # Goodness of fit measures: extract & average
    r2 = avg_func(fg.get_params('r_squared'))
    error = avg_func(fg.get_params('error'))

    # Collect all results together, to be added to ERPparam object
    results = ERPparamResults(ap_params, peak_params, r2, error, gauss_params)

    # Create the new ERPparam object, with settings, data info & results
    fm = ERPparam()
    fm.add_settings(fg.get_settings())
    fm.add_meta_data(fg.get_meta_data())
    fm.add_results(results)

    # Generate the average model from the parameters
    if regenerate:
        fm._regenerate_model()

    return fm


def combine_ERPparams(ERPparams):
    """Combine a group of ERPparam and/or ERPparamGroup objects into a single ERPparamGroup object.

    Parameters
    ----------
    ERPparams : list of ERPparam or ERPparamGroup
        Objects to be concatenated into a ERPparamGroup.

    Returns
    -------
    fg : ERPparamGroup
        Resultant object from combining inputs.

    Raises
    ------
    IncompatibleSettingsError
        If the input objects have incompatible settings for combining.

    Examples
    --------
    Combine ERPparam objects together (where `fm1`, `fm2` & `fm3` are assumed to be defined and fit):

    >>> fg = combine_ERPparams([fm1, fm2, fm3])  # doctest:+SKIP

    Combine ERPparamGroup objects together (where `fg1` & `fg2` are assumed to be defined and fit):

    >>> fg = combine_ERPparams([fg1, fg2])  # doctest:+SKIP
    """

    # Compare settings
    if not compare_info(ERPparams, 'settings') or not compare_info(ERPparams, 'meta_data'):
        raise IncompatibleSettingsError("These objects have incompatible settings "
                                        "or meta data, and so cannot be combined.")

    # Initialize ERPparamGroup object, with settings derived from input objects
    fg = ERPparamGroup(*ERPparams[0].get_settings(), verbose=ERPparams[0].verbose)

    # Use a temporary store to collect spectra, as we'll only add it if it is consistently present
    #   We check how many frequencies by accessing meta data, in case of no frequency vector
    meta_data = ERPparams[0].get_meta_data()
    n_freqs = len(gen_freqs(meta_data.freq_range, meta_data.freq_res))
    temp_power_spectra = np.empty([0, n_freqs])

    # Add ERPparam results from each ERPparam object to group
    for f_obj in ERPparams:

        # Add ERPparamGroup object
        if isinstance(f_obj, ERPparamGroup):
            fg.group_results.extend(f_obj.group_results)
            if f_obj.power_spectra is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, f_obj.power_spectra])

        # Add ERPparam object
        else:
            fg.group_results.append(f_obj.get_results())
            if f_obj.power_spectrum is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, f_obj.power_spectrum])

    # If the number of collected power spectra is consistent, then add them to object
    if len(fg) == temp_power_spectra.shape[0]:
        fg.power_spectra = temp_power_spectra

    # Set the check data mode, as True if any of the inputs have it on, False otherwise
    fg.set_check_data_mode(any(getattr(f_obj, '_check_data') for f_obj in ERPparams))

    # Add data information information
    fg.add_meta_data(ERPparams[0].get_meta_data())

    return fg


def fit_ERPparam_3d(fg, freqs, power_spectra, freq_range=None, n_jobs=1):
    """Fit ERPparam models across a 3d array of power spectra.

    Parameters
    ----------
    fg : ERPparamGroup
        Object to fit with, initialized with desired settings.
    freqs : 1d array
        Frequency values for the power spectra, in linear space.
    power_spectra : 3d array
        Power values, in linear space, with shape as: [n_conditions, n_power_spectra, n_freqs].
    freq_range : list of [float, float], optional
        Desired frequency range to fit. If not provided, fits the entire given range.
    n_jobs : int, optional, default: 1
        Number of jobs to run in parallel.
        1 is no parallelization. -1 uses all available cores.

    Returns
    -------
    fgs : list of ERPparamGroups
        Collected ERPparamGroups after fitting across power spectra, length of n_conditions.


    Examples
    --------
    Fit a 3d array of power spectra, assuming `freqs` and `spectra` are already defined:

    >>> from ERPparam import ERPparamGroup
    >>> fg = ERPparamGroup(peak_width_limits=[1, 6], min_peak_height=0.1)
    >>> fgs = fit_ERPparam_3d(fg, freqs, power_spectra, freq_range=[3, 30])  # doctest:+SKIP
    """

    # Reshape 3d data to 2d and fit, in order to fit with a single group model object
    shape = np.shape(power_spectra)
    powers_2d = np.reshape(power_spectra, (shape[0] * shape[1], shape[2]))

    fg.fit(freqs, powers_2d, freq_range, n_jobs)

    # Reorganize 2d results into a list of model group objects, to reflect original shape
    fgs = [fg.get_group(range(dim_a * shape[1], (dim_a + 1) * shape[1])) \
        for dim_a in range(shape[0])]

    return fgs
