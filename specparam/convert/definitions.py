"""Define parameter converters."""

from specparam.convert.params import compute_peak_height

###################################################################################################
## DEFINE DEFAULT CONVERTERS

DEFAULT_CONVERTERS = {
    'aperiodic' : {'offset' : None, 'exponent' : None},
    'periodic' : {'cf' : None, 'pw' : 'log_sub', 'bw' : 'full_width'},
}

###################################################################################################
## PRE-DEFINED CONVERTERS

CONVERTERS = {

    'aperiodic' : {

        'offset' : {},
        'exponent' : {},

    },

    'periodic' : {

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

###################################################################################################
## NULL CONVERTERS: extract the fit parameter, with no conversion applied

NULL_CONVERTERS = {
    'aperiodic' : lambda param, model : \
        model.results.params.aperiodic._fit[model.modes.aperiodic.params.indices[param]],
    'periodic' : lambda param, model, peak_ind : \
        model.results.params.periodic._fit[peak_ind, model.modes.periodic.params.indices[param]],
}

###################################################################################################
## SELECTOR

def get_converter(component, parameter, converter):
    """Get a specified parameter converter function.

    Parameters
    ----------
    component : {'aperiodic', 'periodic'}
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
