"""Define fitting modes."""

from collections import OrderedDict

from specparam.modes.mode import Mode
from specparam.modes.params import ParamDefinition
from specparam.modes.funcs import (expo_function, expo_nk_function, double_expo_function,
                                   gaussian_function, skewnorm_function, cauchy_function)
from specparam.modes.jacobians import jacobian_gauss

###################################################################################################
## APERIODIC MODES

# Fixed
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
    freq_space='linear',
    powers_space='log10',
)


# Knee
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
    freq_space='linear',
    powers_space='log10',
)


# Double exponent
params_double_exp = ParamDefinition(OrderedDict({
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
    params=params_double_exp,
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

# Gaussian
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
    freq_space='linear',
    powers_space='log10',
)


# Skewed Gaussian
params_skew = ParamDefinition(OrderedDict({
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
    'skew' : 'Skewness of the peak.',
}))

pe_skewnorm = Mode(
    name='skewnorm',
    component='periodic',
    description='Skewed Gaussian peak fit function.',
    func=skewnorm_function,
    jacobian=None,
    params=params_skew,
    freq_space='linear',
    powers_space='log10',
)


# Cauchy
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
    freq_space='linear',
    powers_space='log10',
)


# Collect available periodic modes
PE_MODES = {
    'gaussian' : pe_gaussian,
    'skewed_gaussian' : pe_skewnorm,
    'cauchy' : pe_cauchy,
}
