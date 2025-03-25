"""Internal functions to manage info related to model objects."""

###################################################################################################
###################################################################################################

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

    # TEMP / TEST:
    aperiodic_mode = str(aperiodic_mode)

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

    # TEMP / TEST:
    aperiodic_mode = str(aperiodic_mode)

    # Get the periodic indices, and then update dictionary with aperiodic ones
    indices = get_peak_indices()
    indices.update(get_ap_indices(aperiodic_mode))

    return indices


# TEMP: TO DROP?
# def get_info(model_obj, aspect):
#     """Get a selection of information from a model objects.

#     Parameters
#     ----------
#     model_obj : SpectralModel or SpectralGroupModel
#         Object to get attributes from.
#     aspect : {'settings', 'meta_data', 'results'}
#         Which set of attributes to compare the objects across.

#     Returns
#     -------
#     dict
#         The set of specified info from the model object.
#     """

#     return {key : getattr(model_obj, key) for key in get_description()[aspect]}
