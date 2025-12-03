"""Define fitting modes."""

from functools import partial
from collections import OrderedDict

from specparam.modes.mode import Mode
from specparam.modes.params import ParamDefinition
from specparam.modes.funcs import (expo_function, expo_nk_function, double_expo_function,
                                   gaussian_function, skewed_gaussian_function, cauchy_function)
from specparam.modes.jacobians import jacobian_gauss
from specparam.utils.checks import check_selection

###################################################################################################
## APERIODIC MODES

## AP - Fixed Mode

params_fixed = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}))

ap_fixed = Mode(
    name='fixed',
    component='aperiodic',
    description='Fit an exponential, with no knee.',
    func=expo_nk_function,
    jacobian=None,
    params=params_fixed,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)


## AP - Knee Mode

params_knee = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}))

ap_knee = Mode(
    name='knee',
    component='aperiodic',
    description='Fit an exponential, with a knee.',
    func=expo_function,
    jacobian=None,
    params=params_knee,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)


## AP - Double Exponent Mode

params_doublexp = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'exponent0' : 'Exponent of the aperiodic component, before the knee.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent1' : 'Exponent of the aperiodic component, after the knee.',
}))

ap_doublexp = Mode(
    name='doublexp',
    component='aperiodic',
    description='Fit an function with 2 exponents and a knee.',
    func=double_expo_function,
    jacobian=None,
    params=params_doublexp,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)


# Collect available aperiodic modes
AP_MODES = {
    'fixed' : ap_fixed,
    'knee' : ap_knee,
    'doublexp' : ap_doublexp,
}

###################################################################################################
## PERIODIC MODES

## PE - Gaussian Mode

params_gauss = ParamDefinition(OrderedDict({
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
}))

pe_gaussian = Mode(
    name='gaussian',
    component='periodic',
    description='Gaussian peak fit function.',
    func=gaussian_function,
    jacobian=jacobian_gauss,
    params=params_gauss,
    ndim=2,
    freq_space='linear',
    powers_space='log10',
)


## PE - Skewed Gaussian Mode

params_skewed_gaussian = ParamDefinition(OrderedDict({
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
    'skew' : 'Skewness of the peak.',
}))

pe_skewed_gaussian = Mode(
    name='skewed_gaussian',
    component='periodic',
    description='Skewed Gaussian peak fit function.',
    func=skewed_gaussian_function,
    jacobian=None,
    params=params_skewed_gaussian,
    ndim=2,
    freq_space='linear',
    powers_space='log10',
)


## PE - Cauchy Mode

params_cauchy = ParamDefinition(OrderedDict({
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
}))

pe_cauchy = Mode(
    name='cauchy',
    component='periodic',
    description='Cauchy peak fit function.',
    func=cauchy_function,
    jacobian=None,
    params=params_cauchy,
    ndim=2,
    freq_space='linear',
    powers_space='log10',
)


# Collect available periodic modes
PE_MODES = {
    'gaussian' : pe_gaussian,
    'skewed_gaussian' : pe_skewed_gaussian,
    'cauchy' : pe_cauchy,
}

###################################################################################################
## ALL MODES

# Collect a store of all available modes
MODES = {
    'aperiodic' : AP_MODES,
    'periodic' : PE_MODES,
}

###################################################################################################
## CHECKER FUNCTION

def check_modes(component, check_params=False):
    """Check the set of modes that are available.

    Parameters
    ----------
    component : {'aperiodic', 'periodic'}
        Which component to check available modes for.
    check_params : bool, optional, default: False
        Whether to print out information on the parameters of each mode.
    """

    print('Available {:s} modes:'.format(component))
    for mode in MODES[component].values():
        if not check_params:
            print('    {:10s}    {:s}'.format(mode.name, mode.description))
        else:
            print('\n{:s}'.format(mode.name))
            print('    {:s}'.format(mode.description))
            mode.check_params()


check_mode_definition = partial(check_selection, definition=Mode)
