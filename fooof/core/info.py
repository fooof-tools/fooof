"""Internal functions to manage info related to FOOOF objects."""

###################################################################################################
###################################################################################################

def get_description():
    """Get dictionary specifying FOOOF attributes, and what kind of data they store.

    Returns
    -------
    attributes : dict
        Mapping of FOOOF object attributes, and what kind of data they are.

    Notes
    -----
    This function organizes public FOOOF object attributes into:

    - results : parameters for and measures of the model
    - settings : model settings
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
                  'data' : ['power_spectrum', 'freq_range', 'freq_res'],
                  'meta_data' : ['freq_range', 'freq_res'],
                  'arrays' : ['freqs', 'power_spectrum', 'aperiodic_params_',
                              'peak_params_', 'gaussian_params_'],
                  'model_components' : ['fooofed_spectrum_', '_spectrum_flat',
                                        '_spectrum_peak_rm', '_ap_fit', '_peak_fit'],
                  'descriptors' : ['has_data', 'has_model', 'n_peaks_']
                  }

    return attributes


def get_indices(aperiodic_mode):
    """Get a dictionary mapping indices of FOOOF params to column labels.

    Parameters
    ----------
    aperiodic_mode : {'fixed', 'knee'}
        Which approach taken to fit the aperiodic component.

    Returns
    -------
    indices : dict
        Mapping of the column indices for the FOOOF model fit params.
    """

    indices = {
        'CF' : 0,
        'PW' : 1,
        'BW' : 2,
        'offset' : 0,
        'knee' : 1 if aperiodic_mode == 'knee' else None,
        'exponent' : 1 if aperiodic_mode == 'fixed' else 2
    }

    return indices
