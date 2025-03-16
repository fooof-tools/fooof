"""Define fitting modes"""

from specparam.modes.mode import Mode
from specparam.modes.funcs import (expo_function, expo_nk_function, double_expo_function,
                                   gaussian_function, skewnorm_function)
from specparam.modes.jacobians import jacobian_gauss

###################################################################################################
## APERIODIC MODES

# Fixed
param_desc_fixed = {
    'offset' : 'Offset of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}
ap_fixed = Mode(
    name='fixed',
    component='aperiodic',
    description='Fit an exponential, with no knee.',
    func=expo_nk_function,
    jacobian=None,
    params=['offset', 'exponent'],
    param_description=param_desc_fixed,
    freq_space='linear',
    powers_space='log10',
)


# Knee
param_desc_knee = {
    'offset' : 'Offset of the aperiodic component.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}

ap_knee = Mode(
    name='knee',
    component='aperiodic',
    description='Fit an exponential, with a knee.',
    func=expo_function,
    jacobian=None,
    params=['offset', 'knee', 'exponent'],
    param_description=param_desc_knee,
    freq_space='linear',
    powers_space='log10',
)


# Double exponent
param_desc = {
    'offset' : 'Offset of the aperiodic component.',
    'exponent0' : 'Exponent of the aperiodic component, before the knee.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent1' : 'Exponent of the aperiodic component, after the knee.',
    }

ap_doublexp = Mode(
    name='doublexp',
    component='aperiodic',
    description='Fit an function with 2 exponents and a knee.',
    func=double_expo_function,
    jacobian=None,
    params=['offset', 'exponent0', 'knee', 'exponent1'],
    param_description=param_desc,
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
param_desc_gaus = {
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
}

pe_gaussian = Mode(
    name='gaussian',
    component='periodic',
    description='Gaussian peak fit function.',
    func=gaussian_function,
    jacobian=jacobian_gauss,
    params=['cf', 'pw', 'bw'],
    param_description=param_desc_gaus,
    freq_space='linear',
    powers_space='log10',
)


# Skewed Gaussian
param_desc_skew = {
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
    'skew' : 'Skewness of the peak.',
    }

pe_skewnorm = Mode(
    name='skewnorm',
    component='periodic',
    description='Skewed Gaussian peak fit function.',
    func=skewnorm_function,
    jacobian=None,
    params=['cf', 'pw', 'bw', 'skew'],
    param_description=param_desc_skew,
    freq_space='linear',
    powers_space='log10',
)

# Collect available periodic modes
PE_MODES = {
    'gaussian' : pe_gaussian,
    'skewed_gaussian' : pe_skewnorm,
}
