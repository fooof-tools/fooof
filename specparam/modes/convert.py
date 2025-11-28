"""Parameter converters.

Notes
-----
Parameter converters should have the following properties, depending on component:
- for 'peak' parameters : callable, takes 'param' & 'model', 'peak_ind' as inputs
- for 'aperiodic' parameters : callable, takes 'param' & 'model' as inputs
"""

import numpy as np

from specparam.utils.select import nearest_ind

###################################################################################################
###################################################################################################

## NULL CONVERTERS: extract the fit parameter, with no conversion applied

NULL_CONVERTERS = {
    'aperiodic' : lambda param, model : \
        model.results.params.aperiodic._fit[model.modes.aperiodic.params.indices[param]],
    'peak' : lambda param, model, peak_ind : \
        model.results.params.periodic._fit[peak_ind, model.modes.periodic.params.indices[param]],
}

## PRE-DEFINED CONVERTERS

CONVERTERS = {
    'aperiodic' : {
        'offset' : {},
        'exponent' : {},
    },
    'peak' : {
        'cf' : {},
        'pw' : {
            'log_sub' : lambda param, model, peak_ind : \
                compute_peak_height(model, peak_ind, 'log', 'subtract'),
            'log_div' : lambda param, model, peak_ind : \
                compute_peak_height(model, peak_ind, 'log', 'divide'),
            'lin_sub' : lambda param, model, peak_ind : \
                compute_peak_height(model, peak_ind, 'linear', 'subtract'),
            'lin_div' : lambda param, model, peak_ind : \
                compute_peak_height(model, peak_ind, 'linear', 'divide'),
        },
        'bw' : {
            'full_width' : lambda param, model, peak_ind : \
                2 * model.results.params.periodic._fit[\
                        peak_ind, model.modes.periodic.params.indices['bw']]
        },
    }
}


## DEFINE DEFAULT CONVERTERS

DEFAULT_CONVERTERS = {
    'aperiodic' : {'offset' : None, 'exponent' : None},
    'peak' : {'cf' : None, 'pw' : 'log_sub', 'bw' : 'full_width'},
}

## CONVERTER FUNCTIONS

def get_converter(component, parameter, converter):
    """Get a specified parameter converter function.

    Parameters
    ----------
    component : {'aperiodic', 'peak'}
        Which component to access a converter for.
    parameter : str
        The name of the parameter to access a converter for.
    converter : str or callable
        The converter to access.
        If str, should correspond to a built-in converter.
        If callable, should be a custom converter definition, following framework.

    Returns
    -------
    converter : callable
        Function to compute parameter conversion.

    Notes
    -----
    This function accesses predefined converters from `CONVERTERS`.
    If a callable, as a custom definition, is passed in, the same callable is returned.
    If the parameter or converter name is not found, a null converter
    (from `NULL_CONVERTERS`) is returned.
    """

    if isinstance(converter, str) and converter in CONVERTERS[component][parameter]:
        converter = CONVERTERS[component][parameter][converter]
    elif callable(converter):
        pass
    else:
        converter = NULL_CONVERTERS[component]

    return converter


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
        converted_params[p_ind] = converter(param, model)

    return converted_params


def convert_peak_params(model, updates):
    """Convert peak parameters.

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
        Converted peak parameters.
    """

    converted_params = np.zeros_like(model.results.params.periodic._fit)
    for peak_ind in range(len(converted_params)):
        for param, param_ind in model.modes.periodic.params.indices.items():
            converter = get_converter('peak', param, updates.get(param, None))
            converted_params[peak_ind, param_ind] = converter(param, model, peak_ind)

    return converted_params


## PARAMETER CONVERTERS

PEAK_HEIGHT_OPERATIONS = {
    'subtract' : np.subtract,
    'divide' : np.divide,
}

def compute_peak_height(model, peak_ind, spacing, operation):
    """Compute peak heights, based on specified approach & spacing.

    Parameters
    ----------
    model : SpectralModel
        Model object, post fitting.
    peak_ind : int
        Index of which peak to compute height for.
    spacing : {'log', 'linear'}
        Spacing to extract the data components in.
    operation : {'subtract', 'divide'}
        Approach to take to compute the peak height measure.

    Returns
    -------
    peak_height : float
        Computed peak height.
    """

    ind = nearest_ind(model.data.freqs, model.results.params.periodic._fit[\
                          peak_ind, model.modes.periodic.params.indices['cf']])
    peak_height = PEAK_HEIGHT_OPERATIONS[operation](\
        model.results.model.get_component('full', spacing)[ind],
        model.results.model.get_component('aperiodic', spacing)[ind])

    return peak_height
