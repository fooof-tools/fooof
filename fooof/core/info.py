"""Internal functions to manage info related to FOOOF objects."""

def get_obj_desc():
    """Get dictionary specifying FOOOF object names and kind of attributes.

    Returns
    -------
    attibutes : dict
        Mapping of FOOOF object attributes, and what kind of data they are.
    """

    attributes = {'results' : ['aperiodic_params_', 'peak_params_',
                               'r_squared_', 'error_',
                               '_gaussian_params'],
                  'settings' : ['peak_width_limits', 'max_n_peaks',
                                'min_peak_amplitude', 'peak_threshold',
                                'aperiodic_mode'],
                  'data' : ['power_spectrum', 'freq_range', 'freq_res'],
                  'data_info' : ['freq_range', 'freq_res'],
                  'arrays' : ['freqs', 'power_spectrum', 'aperiodic_params_',
                              'peak_params_', '_gaussian_params'],
                  'model_components' : ['_spectrum_flat', '_spectrum_peak_rm',
                                        '_ap_fit', '_peak_fit']}

    return attributes


def get_data_indices(aperiodic_mode):
    """Get a dictionary mapping the column labels to indices in FOOOF data (FOOOFResults).

    Parameters
    ----------
    aperiodic_mode : {'fixed', 'knee'}
        Which approach taken to fit the aperiodic component.

    Returns
    -------
    indices : dict
        Mapping for data columns to the column indices in which they appear.
    """

    indices = {
        'CF'  : 0,
        'Amp' : 1,
        'BW'  : 2,
        'offset' : 0,
        'knee'      : 1 if aperiodic_mode == 'knee' else None,
        'exponent'  : 1 if aperiodic_mode == 'fixed' else 2
    }

    return indices
