"""Internal functions to manage info related to model objects."""

###################################################################################################
###################################################################################################

def get_description():
    """Get dictionary specifying model object attributes, and what kind of data they store.

    Returns
    -------
    attributes : dict
        Mapping of model object attributes, and what kind of data they are.

    Notes
    -----
    This function organizes public model object attributes into:

    - results : parameters for and measures of the model
    - settings : model settings
    - run_modes: checks performed and errors raised
    - data : input data
    - meta_data : meta data of the inputs
    - arrays : data stored in arrays
    - model_components : component pieces of the model
    - descriptors : descriptors of the object status and model results
    """

    attributes = {'results' : ['aperiodic_params_', 'gaussian_params_', 'peak_params_',
                               'r_squared_', 'error_'],
                  'settings' : ['peak_width_limits', 'max_n_peaks',
                                'min_peak_height', 'peak_threshold',
                                'aperiodic_mode'],
                  'run_modes': ['_debug', '_check_freqs', '_check_data'],
                  'data' : ['power_spectrum', 'freq_range', 'freq_res'],
                  'meta_data' : ['freq_range', 'freq_res'],
                  'arrays' : ['freqs', 'power_spectrum', 'aperiodic_params_',
                              'peak_params_', 'gaussian_params_'],
                  'model_components' : ['modeled_spectrum_', '_spectrum_flat',
                                        '_spectrum_peak_rm', '_ap_fit', '_peak_fit'],
                  'descriptors' : ['has_data', 'has_model', 'n_peaks_']
                  }

    return attributes


def get_peak_indices():
    """Get a mapping from column labels to indices for peak parameters.

    Returns
    -------
    indices : dict
        Mapping of the column labels and indices for the peak parameters.
    """

    indices = {
        'CF' : 0,
        'PW' : 1,
        'BW' : 2,
    }

    return indices


def get_ap_indices(aperiodic_mode):
    """Get a mapping from column labels to indices for aperiodic parameters.

    Parameters
    ----------
    aperiodic_mode : {'fixed', 'knee'}
        Which mode was used for the aperiodic component.

    Returns
    -------
    indices : dict
        Mapping of the column labels and indices for the aperiodic parameters.
    """

    if aperiodic_mode == 'fixed':
        labels = ('offset', 'exponent')
    elif aperiodic_mode == 'knee':
        labels = ('offset', 'knee', 'exponent')
    else:
        raise ValueError("Aperiodic mode not understood.")

    indices = {label : index for index, label in enumerate(labels)}

    return indices


def get_indices(aperiodic_mode):
    """Get a mapping from column labels to indices for all parameters.

    Parameters
    ----------
    aperiodic_mode : {'fixed', 'knee'}
        Which mode was used for the aperiodic component.

    Returns
    -------
    indices : dict
        Mapping of the column labels and indices for all parameters.
    """

    # Get the periodic indices, and then update dictionary with aperiodic ones
    indices = get_peak_indices()
    indices.update(get_ap_indices(aperiodic_mode))

    return indices


def get_info(model_obj, aspect):
    """Get a selection of information from a model objects.

    Parameters
    ----------
    model_obj : SpectralModel or SpectralGroupModel
        Object to get attributes from.
    aspect : {'settings', 'meta_data', 'results'}
        Which set of attributes to compare the objects across.

    Returns
    -------
    dict
        The set of specified info from the model object.
    """

    return {key : getattr(model_obj, key) for key in get_description()[aspect]}
