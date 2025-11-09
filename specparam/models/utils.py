"""Utility functions for managing and manipulating model objects."""

import numpy as np

from specparam.sim import gen_freqs
from specparam.data.stores import FitResults
from specparam.utils.checks import check_input_options
from specparam.models import (SpectralModel, SpectralGroupModel,
                              SpectralTimeModel, SpectralTimeEventModel)
from specparam.data.periodic import get_band_peak_group
from specparam.modutils.errors import NoModelError, IncompatibleSettingsError

###################################################################################################
###################################################################################################

# Collect dictionary of all available models
MODELS = {
    'model' : SpectralModel,
    'group' : SpectralGroupModel,
    'time' : SpectralTimeModel,
    'event' : SpectralTimeEventModel,
}


def initialize_model_from_source(source, target):
    """Initialize a model object based on a source model object.

    Parameters
    ----------
    source : SpectralModel or Spectral*Model
        Model object to initialize from.
    target : {'model', 'group', 'time', 'event'}
        Type of model object to initialize.

    Returns
    -------
    model : Spectral*Model
        Model object, of type `target`, initialized from source.
    """

    model = MODELS[target](**source.modes.get_modes()._asdict(),
                           **source.algorithm.settings.values,
                           metrics=source.results.metrics.labels,
                           bands=source.results.bands,
                           verbose=source.verbose)
    model.data.add_meta_data(source.data.get_meta_data())
    model.data.set_checks(*source.data.get_checks())
    model.algorithm.set_debug(source.algorithm.get_debug())

    return model


def compare_model_objs(model_objs, aspect):
    """Compare multiple model, checking for consistent attributes.

    Parameters
    ----------
    model_objs : list of SpectralModel and/or SpectralGroupModel
        Objects whose attributes are to be compared.
    aspect : {'settings', 'meta_data', 'metrics'} or list
        Which set of attributes to compare the objects across.

    Returns
    -------
    consistent : bool
        Whether the settings are consistent across the input list of objects.
    """

    if isinstance(aspect, list):
        outputs = []
        for caspect in aspect:
            outputs.append(compare_model_objs(model_objs, caspect))
        return np.all(outputs)

    aspects = ['modes', 'settings', 'meta_data', 'bands', 'metrics']
    check_input_options(aspect, aspects, 'aspect')

    # Check specified aspect of the objects are the same across instances
    for m_obj_1, m_obj_2 in zip(model_objs[:-1], model_objs[1:]):
        if aspect == 'modes':
            consistent = m_obj_1.modes.get_modes() == m_obj_2.modes.get_modes()
        if aspect == 'settings':
            consistent = m_obj_1.algorithm.get_settings() == m_obj_2.algorithm.get_settings()
        if aspect == 'meta_data':
            consistent = m_obj_1.data.get_meta_data() == m_obj_2.data.get_meta_data()
        if aspect == 'bands':
            consistent = m_obj_1.results.bands == m_obj_2.results.bands
        if aspect == 'metrics':
            consistent = m_obj_1.results.metrics.labels == m_obj_2.results.metrics.labels

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

    if not group.results.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    avg_funcs = {'mean' : np.nanmean, 'median' : np.nanmedian}
    if avg_method not in avg_funcs.keys():
        raise ValueError("Requested average method not understood.")

    # Aperiodic parameters: extract & average
    ap_params = avg_funcs[avg_method](group.results.get_params('aperiodic'), 0)

    # Periodic parameters: extract & average
    peak_fit_params = []
    peak_conv_params = []

    for band_def in bands.definitions:

        peaks_fit = get_band_peak_group(group, band_def, attribute='fit')
        peaks_conv = get_band_peak_group(group, band_def, attribute='converted')

        # Check if there are any extracted peaks - if not, don't add
        #   Note that we only check fit peaks, but converted should be the same
        if not np.all(np.isnan(peaks_fit)):
            peak_fit_params.append(avg_funcs[avg_method](peaks_fit, 0))
            peak_conv_params.append(avg_funcs[avg_method](peaks_conv, 0))

    # Collect together result parameters
    results_params = {
        'aperiodic_fit' : ap_params,
        'aperiodic_converted' : np.array([np.nan] * len(ap_params)),
        'peak_fit' : np.array(peak_fit_params),
        'peak_converted' : np.array(peak_conv_params),
    }

    # Goodness of fit measures: extract & average
    results_metrics = {label : avg_funcs[avg_method](group.results.get_metrics(label)) \
        for label in group.results.metrics.labels}

    # Create the new model object, with settings, data info, and then add average results
    model = group.get_model()
    model.results.add_results(FitResults(**results_params, metrics=results_metrics))

    # Generate the average model from the parameters
    if regenerate:
        model.results._regenerate_model(group.data.freqs)

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

    if not group.results.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    avg_funcs = {'mean' : np.nanmean, 'median' : np.nanmedian}
    if avg_method not in avg_funcs.keys():
        raise ValueError("Requested average method not understood.")

    models = np.zeros(shape=group.data.power_spectra.shape)
    for ind in range(len(group.results)):
        models[ind, :] = group.get_model(ind, regenerate=True).results.model.modeled_spectrum

    avg_model = avg_funcs[avg_method](models, 0)

    return group.data.freqs, avg_model


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
    group = SpectralGroupModel(**model_objs[0].modes.get_modes()._asdict(),
                               **model_objs[0].algorithm.get_settings()._asdict(),
                               verbose=model_objs[0].verbose)

    # Use a temporary store to collect spectra, as we'll only add it if it is consistently present
    #   We check how many frequencies by accessing meta data, in case of no frequency vector
    meta_data = model_objs[0].data.get_meta_data()
    n_freqs = len(gen_freqs(meta_data.freq_range, meta_data.freq_res))
    temp_power_spectra = np.empty([0, n_freqs])

    # Add results from each model object to group
    for m_obj in model_objs:

        # Add group object
        if isinstance(m_obj, SpectralGroupModel):
            group.results.group_results.extend(m_obj.results.group_results)
            if m_obj.data.power_spectra is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, m_obj.data.power_spectra])

        # Add model object
        else:
            group.results.group_results.append(m_obj.results.get_results())
            if m_obj.data.power_spectrum is not None:
                temp_power_spectra = np.vstack([temp_power_spectra, m_obj.data.power_spectrum])

    # If the number of collected power spectra is consistent, then add them to object
    if len(group.results) == temp_power_spectra.shape[0]:
        group.data.power_spectra = temp_power_spectra

    # Set the status for freqs & data checking
    #  Check states gets set as True if any of the inputs have it on, False otherwise
    group.data.set_checks(\
        check_freqs=any(m_obj.data.checks['freqs'] for m_obj in model_objs),
        check_data=any(m_obj.data.checks['data'] for m_obj in model_objs))

    # Add data information information
    group.data.add_meta_data(model_objs[0].data.get_meta_data())

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
