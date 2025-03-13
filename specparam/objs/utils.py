"""Utility functions for managing and manipulating model objects."""

import numpy as np

from specparam.sim import gen_freqs
from specparam.data import FitResults
from specparam.objs import SpectralModel, SpectralGroupModel
from specparam.data.periodic import get_band_peak_group
from specparam.modutils.errors import NoModelError, IncompatibleSettingsError

###################################################################################################
###################################################################################################

def compare_model_objs(model_objs, aspect):
    """Compare multiple model, checking for consistent attributes.

    Parameters
    ----------
    model_objs : list of SpectralModel and/or SpectralGroupModel
        Objects whose attributes are to be compared.
    aspect : {'settings', 'meta_data'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    consistent : bool
        Whether the settings are consistent across the input list of objects.
    """

    # Check specified aspect of the objects are the same across instances
    for m_obj_1, m_obj_2 in zip(model_objs[:-1], model_objs[1:]):
        if getattr(m_obj_1, 'get_' + aspect)() != getattr(m_obj_2, 'get_' + aspect)():
            consistent = False
            break
    else:
        consistent = True

    return consistent


def average_group(group, bands, avg_method='mean', regenerate=True):
    """Average across model fits in a group model object.

    Parameters
    ----------
    group : SpectralGroupModel
        Object with model fit results to average across.
    bands : Bands
        Bands object that defines the frequency bands to collapse peaks across.
    avg : {'mean', 'median'}
        Averaging function to use.
    regenerate : bool, optional, default: True
        Whether to regenerate the model for the averaged parameters.

    Returns
    -------
    model : SpectralModel
        Object containing the average model results.

    Raises
    ------
    ValueError
        If the requested averaging method is not understood.
    NoModelError
        If there are no model fit results available to average across.
    """

    if not group.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    avg_funcs = {'mean' : np.nanmean, 'median' : np.nanmedian}
    if avg_method not in avg_funcs.keys():
        raise ValueError("Requested average method not understood.")

    # Aperiodic parameters: extract & average
    ap_params = avg_funcs[avg_method](group.get_params('aperiodic_params'), 0)

    # Periodic parameters: extract & average
    peak_params = []
    gauss_params = []

    for band_def in bands.definitions:

        peaks = get_band_peak_group(group, band_def, attribute='peak_params')
        gauss = get_band_peak_group(group, band_def, attribute='gaussian_params')

        # Check if there are any extracted peaks - if not, don't add
        #   Note that we only check peaks, but gauss should be the same
        if not np.all(np.isnan(peaks)):
            peak_params.append(avg_funcs[avg_method](peaks, 0))
            gauss_params.append(avg_funcs[avg_method](gauss, 0))

    peak_params = np.array(peak_params)
    gauss_params = np.array(gauss_params)

    # Goodness of fit measures: extract & average
    r2 = avg_funcs[avg_method](group.get_params('r_squared'))
    error = avg_funcs[avg_method](group.get_params('error'))

    # Collect all results together, to be added to the model object
    results = FitResults(ap_params, peak_params, r2, error, gauss_params)

    # Create the new model object, with settings, data info & results
    model = SpectralModel()
    model.add_settings(group.get_settings())
    model.add_meta_data(group.get_meta_data())
    model.add_results(results)

    # Generate the average model from the parameters
    if regenerate:
        model._regenerate_model()

    return model


def average_reconstructions(group, avg_method='mean'):
    """Average across model reconstructions for a group of power spectra.

    Parameters
    ----------
    group : SpectralGroupModel
        Object with model fit results to average across.
    avg : {'mean', 'median'}
        Averaging function to use.

    Returns
    -------
    freqs : 1d array
        Frequency values for the average model reconstruction.
    avg_model : 1d array
        Power values for the average model reconstruction.
        Note that power values are in log10 space.
    """

    if not group.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    avg_funcs = {'mean' : np.nanmean, 'median' : np.nanmedian}
    if avg_method not in avg_funcs.keys():
        raise ValueError("Requested average method not understood.")

    models = np.zeros(shape=group.power_spectra.shape)
    for ind in range(len(group)):
        models[ind, :] = group.get_model(ind, regenerate=True).modeled_spectrum_

    avg_model = avg_funcs[avg_method](models, 0)

    return group.freqs, avg_model


def combine_model_objs(model_objs):
    """Combine a group of model objects into a single group model object.

    Parameters
    ----------
    model_objs : list of SpectralModel or SpectralGroupModel
        Objects to be concatenated into a group model object.

    Returns
    -------
    group : SpectralGroupModel
        Resultant object from combining inputs.

    Raises
    ------
    IncompatibleSettingsError
        If the input objects have incompatible settings for combining.

    Examples
    --------
    Combine model objects together (where `fm1`, `fm2` & `fm3` are assumed to be defined and fit):

    >>> group = combine_model_objs([fm1, fm2, fm3])  # doctest:+SKIP

    Combine group model objects together (where `fg1` & `fg2` are assumed to be defined and fit):

    >>> group = combine_model_objs([fg1, fg2])  # doctest:+SKIP
    """

    # Compare settings
    if not compare_model_objs(model_objs, 'settings') \
        or not compare_model_objs(model_objs, 'meta_data'):
        raise IncompatibleSettingsError("These objects have incompatible settings "
                                        "or meta data, and so cannot be combined.")

    # Initialize group model object, with settings derived from input objects
    group = SpectralGroupModel(*model_objs[0].get_settings(), verbose=model_objs[0].verbose)

    # Use a temporary store to collect spectra, as we'll only add it if it is consistently present
    #   We check how many frequencies by accessing meta data, in case of no frequency vector
    meta_data = model_objs[0].get_meta_data()
    n_freqs = len(gen_freqs(meta_data.freq_range, meta_data.freq_res))
    temp_power_spectra = np.empty([0, n_freqs])

    # Add results from each model object to group
    for m_obj in model_objs:

        # Add group object
        if isinstance(m_obj, SpectralGroupModel):
            group.group_results.extend(m_obj.group_results)
            if m_obj.power_spectra is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, m_obj.power_spectra])

        # Add model object
        else:
            group.group_results.append(m_obj.get_results())
            if m_obj.power_spectrum is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, m_obj.power_spectrum])

    # If the number of collected power spectra is consistent, then add them to object
    if len(group) == temp_power_spectra.shape[0]:
        group.power_spectra = temp_power_spectra

    # Set the check data mode, as True if any of the inputs have it on, False otherwise
    group.set_check_modes(\
        check_freqs=any(getattr(m_obj, '_check_freqs') for m_obj in model_objs),
        check_data=any(getattr(m_obj, '_check_data') for m_obj in model_objs))

    # Add data information information
    group.add_meta_data(model_objs[0].get_meta_data())

    return group


def fit_models_3d(group, freqs, power_spectra, freq_range=None, n_jobs=1):
    """Fit power spectrum models across a 3d array of power spectra.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to fit with, initialized with desired settings.
    freqs : 1d array
        Frequency values for the power spectra, in linear space.
    power_spectra : 3d array
        Power values, in linear space, with shape as: [n_conditions, n_power_spectra, n_freqs].
    freq_range : list of [float, float], optional
        Frequency range to fit. If not provided, fits the entire given range.
    n_jobs : int, optional, default: 1
        Number of jobs to run in parallel.
        1 is no parallelization. -1 uses all available cores.

    Returns
    -------
    all_models : list of SpectralGroupModel
        Collected model results after fitting across power spectra, length of n_conditions.

    Examples
    --------
    Fit a 3d array of power spectra, assuming `freqs` and `spectra` are already defined:

    >>> from specparam import SpectralGroupModel
    >>> group = SpectralGroupModel(peak_width_limits=[1, 6], min_peak_height=0.1)
    >>> models = fit_models_3d(group, freqs, power_spectra, freq_range=[3, 30])  # doctest:+SKIP
    """

    # Reshape 3d data to 2d and fit, in order to fit with a single group model object
    shape = np.shape(power_spectra)
    powers_2d = np.reshape(power_spectra, (shape[0] * shape[1], shape[2]))

    group.fit(freqs, powers_2d, freq_range, n_jobs)

    # Reorganize 2d results into a list of model group objects, to reflect original shape
    all_models = [group.get_group(range(dim_a * shape[1], (dim_a + 1) * shape[1])) \
        for dim_a in range(shape[0])]

    return all_models
