"""Internal functions to manage info related to model objects."""

###################################################################################################
###################################################################################################

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
