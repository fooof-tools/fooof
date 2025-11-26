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

## NULL UPDATERS: extract the fit parameter, with no conversion applied

NULL_UPDATERS = {
    'aperiodic' : lambda param, model : \
        model.results.params.aperiodic._fit[model.modes.aperiodic.params.indices[param]],
    'peak' : lambda param, model, peak_ind : \
        model.results.params.periodic._fit[peak_ind, model.modes.periodic.params.indices[param]],
}

## PRE-DEFINED CONVERTERS

UPDATERS = {
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

## CONVERTER FUNCTIONS

def get_converter(component, parameter, label):
    """Get a specified parameter converter function.

    Parameters
    ----------
    component : str
        XX
    parameter : str
        XX
    label : str
        XX

    Notes
    -----
    This function accesses predefined converters from `UPDATERS`, defaulting
    to a null converter (`NULL_UPDATERS`) if requested label is None or not found.
    """

    if label and label in UPDATERS[component][parameter]:
        converter = UPDATERS[component][parameter][label]
    else:
        converter = NULL_UPDATERS[component]

    return converter


def convert_aperiodic_params(model, updates):
    """Convert aperiodic parameters."""

    converted_params = np.zeros_like(model.results.params.aperiodic._fit)
    for param, p_ind in model.modes.aperiodic.params.indices.items():
        converter = get_converter('aperiodic', param, updates[param])
        converted_params[p_ind] = converter(param, model)

    return converted_params


def convert_peak_params(model, updates):
    """Convert peak parameters."""

    converted_params = np.zeros_like(model.results.params.periodic._fit)
    for peak_ind in range(len(converted_params)):
        for param, param_ind in model.modes.periodic.params.indices.items():
            converter = get_converter('peak', param, updates.get(param, None))
            converted_params[peak_ind, param_ind] = converter(param, model, peak_ind)

    return converted_params


## PARAMETER CONVERTERS

FUNCS = {
    'subtract' : np.subtract,
    'divide' : np.divide,
}

def compute_peak_height(model, peak_ind, spacing, operation):
    """Compute peak heights, based on specified approach & spacing.

    Parameters
    ----------
    model : SpectralModel
        Model object, post fitting.
    spacing : {'log', 'linear'}
        Spacing to extract the data components in.
    operation : {'subtract', 'divide'}
        Approach to take to compute the peak height measure.
    """

    ind = nearest_ind(model.data.freqs, model.results.params.periodic._fit[\
                          peak_ind, model.modes.periodic.params.indices['cf']])
    out = FUNCS[operation](model.results.model.get_component('full', spacing)[ind],
                           model.results.model.get_component('aperiodic', spacing)[ind])

    return out
