"""Define parameter converters."""

from copy import deepcopy

from specparam.convert.converter import AperiodicParamConverter, PeriodicParamConverter
from specparam.convert.params import compute_peak_height

###################################################################################################
## DEFINE DEFAULT CONVERTERS

DEFAULT_CONVERTERS = {
    'aperiodic' : {'offset' : None, 'exponent' : None},
    'periodic' : {'cf' : None, 'pw' : 'log_sub', 'bw' : 'full_width'},
}


def update_converters(defaults, updates):
    """Update default converters.

    Parameters
    ----------
    defaults : dict
        Default converters.
    updates : dict
        Converter definitions to update.

    Returns
    -------
    converters : dict
        Updated converters definition.
    """

    out = deepcopy(defaults)
    for component, converters in updates.items():
        for param, converter in converters.items():
            out[component][param] = converter

    return out

###################################################################################################
## APERIODIC PARAMETER CONVERTERS

## AP - Null converter
ap_null = AperiodicParamConverter(
    parameter=None,
    name='ap_null',
    description='Null converter for aperiodic converter - return fit parameter value.',
    function=lambda fit_value, model : fit_value,
)

###################################################################################################
## PERIODIC PARAMETER CONVERTERS

## PE - Null converter
pe_null = PeriodicParamConverter(
    parameter=None,
    name='pe_null',
    description='Null converter for aperiodic converter - return fit parameter value.',
    function=lambda fit_value, model, peak_ind : fit_value,
)

## PE - PW

pw_log_sub = PeriodicParamConverter(
    parameter='pw',
    name='log_sub',
    description='Convert peak height to be the log subtraction '\
        'of full model and aperiodic component.',
    function=lambda fit_value, model, peak_ind : \
        compute_peak_height(model, peak_ind, 'log', 'subtract'),
)

pw_log_div = PeriodicParamConverter(
    parameter='pw',
    name='log_div',
    description='Convert peak height to be the log division '\
        'of full model and aperiodic component.',
    function=lambda fit_value, model, peak_ind : \
        compute_peak_height(model, peak_ind, 'log', 'divide'),
)

pw_lin_sub = PeriodicParamConverter(
    parameter='pw',
    name='lin_sub',
    description='Convert peak height to be the linear subtraction '\
        'of full model and aperiodic component.',
    function=lambda fit_value, model, peak_ind : \
        compute_peak_height(model, peak_ind, 'linear', 'subtract'),
)

pw_lin_div = PeriodicParamConverter(
    parameter='pw',
    name='lin_div',
    description='Convert peak height to be the linear division '\
        'of full model and aperiodic component.',
    function=lambda fit_value, model, peak_ind : \
        compute_peak_height(model, peak_ind, 'linear', 'divide'),
)

## PE - BW

bw_full_width = PeriodicParamConverter(
    parameter='bw',
    name='full_width',
    description='Convert peak bandwidth to be the full, '\
        'two-sided bandwidth of the peak.',
    function=lambda fit_value, model, peak_ind : 2 * fit_value,
)

###################################################################################################
## COLLECT ALL CONVERTERS

# Null converters: extract the fit parameter, with no conversion applied
NULL_CONVERTERS = {
    'aperiodic' : ap_null,
    'periodic' : pe_null,
}

# Collect converters by component & by paramter
CONVERTERS = {

    'aperiodic' : {
        'offset' : {},
        'exponent' : {},
    },

    'periodic' : {
        'cf' : {},
        'pw' : {
            'log_sub' : pw_log_sub,
            'log_div' : pw_log_div,
            'lin_sub' : pw_lin_sub,
            'lin_div' : pw_lin_div,
        },
        'bw' : {
            'full_width' : bw_full_width,
        },
    }
}

###################################################################################################
## SELECTOR & CHECKER FUNCTIONS

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


def check_converters(component):
    """Check the set of parameter converters that are available.

    Parameters
    ----------
    component : {'aperiodic', 'periodic'}
        Which component to check available parameter converters for.
    """

    print('Available {:s} converters:'.format(component))
    for param, convs in CONVERTERS[component].items():
        print(param)
        for label, converter in convs.items():
            print('    {:10s}    {:s}'.format(converter.name, converter.description))
