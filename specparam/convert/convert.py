"""Parameter converters.

Notes
-----
Parameter converters should have the following properties, depending on component:
- for 'aperiodic' parameters : callable, takes 'fit_value' & 'model' as inputs
- for 'peak' parameters : callable, takes 'fit_value' & 'model', 'peak_ind' as inputs
"""

import numpy as np

from specparam.convert.definitions import get_converter

###################################################################################################
###################################################################################################

def convert_aperiodic_params(model, updates):
    """Convert aperiodic parameters.

    Parameters
    ----------
    model : SpectralModel
        Model object, post model fitting.
    updates : dict
        Dictionary specifying the parameter conversions to do, whereby:
            Each key is the name of a parameter.
            Each value reflects what conversion to do.
                This can be a string label for a built-in conversion, or a custom implementation.

    Returns
    -------
    converted_parameters : 1d array
        Converted aperiodic parameters.
    """

    converted_params = np.zeros_like(model.results.params.aperiodic._fit)
    for param, p_ind in model.modes.aperiodic.params.indices.items():
        converter = get_converter('aperiodic', param, updates[param])
        fit_value = model.results.params.aperiodic._fit[\
            model.modes.aperiodic.params.indices[param]]
        converted_params[p_ind] = converter(fit_value, model)

    return converted_params


def convert_periodic_params(model, updates):
    """Convert periodic parameters.

    Parameters
    ----------
    model : SpectralModel
        Model object, post model fitting.
    updates : dict
        Dictionary specifying the parameter conversions to do, whereby:
            Each key is the name of a parameter.
            Each value reflects what conversion to do.
                This can be a string label for a built-in conversion, or a custom implementation.

    Returns
    -------
    converted_parameters : array
        Converted periodic parameters.
    """

    converted_params = np.zeros_like(model.results.params.periodic._fit)
    for peak_ind in range(len(converted_params)):
        for param, param_ind in model.modes.periodic.params.indices.items():
            converter = get_converter('periodic', param, updates.get(param, None))
            fit_value = model.results.params.periodic._fit[\
                peak_ind, model.modes.periodic.params.indices[param]]
            converted_params[peak_ind, param_ind] = converter(fit_value, model, peak_ind)

    return converted_params
