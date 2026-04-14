"""Define fitting modes."""

from functools import partial
from collections import OrderedDict

from specparam.modes.mode import Mode
from specparam.modes.params import ParamDefinition
from specparam.modes.funcs import (powerlaw_function, lorentzian_function, double_expo_function,
                                   gaussian_function, skewed_gaussian_function,
                                   cauchy_function, gamma_function, triangle_function)
from specparam.modes.jacobians import jacobian_gauss
from specparam.utils.checks import check_selection

###################################################################################################
## APERIODIC MODES

## AP - Powerlaw (1/f) Mode ('fixed')

params_powerlaw = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}))

ap_powerlaw = Mode(
    name='fixed',
    component='aperiodic',
    description='One-over-f (powerlaw) function.',
    formula=r'A(F) = 10^b * \frac{1}{F^\chi}',
    func=powerlaw_function,
    jacobian=None,
    params=params_powerlaw,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)


## AP - Lorentzian Mode ('knee')

params_lorentzian = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}))

ap_lorentzian = Mode(
    name='knee',
    component='aperiodic',
    description='Lorentzian function, with a powerlaw exponent and a knee.',
    formula=r'A(F) = 10^b * \frac{1}{(k + F^\chi)}',
    func=lorentzian_function,
    jacobian=None,
    params=params_lorentzian,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)


## AP - Double Exponent Mode ('doublexp')

params_doublexp = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'exponent0' : 'Exponent of the aperiodic component, before the knee.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent1' : 'Exponent of the aperiodic component, after the knee.',
}))

ap_doublexp = Mode(
    name='doublexp',
    component='aperiodic',
    description='Multi-fractal powerlaw function with 2 exponents and a knee.',
    formula=r'A(F) = 10^b * \frac{1}{F^{\chi_{0}} * (k + F^{\chi_{1}})}',
    func=double_expo_function,
    jacobian=None,
    params=params_doublexp,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)

## AP - Knee with Constant Mode

params_knee_constant = ParamDefinition(OrderedDict({
    'offset' : 'Offset of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
    'knee' : 'Knee of the aperiodic component.',
    'constant' : 'Constant value which the aperiodic component decays to, after the exponent.',
}))

ap_knee_constant = Mode(
    name='knee_constant',
    component='aperiodic',
    description='Fit a Lorentzian function that decays to a constant.',
    formula=r'XX',
    func=knee_constant_function,
    jacobian=None,
    params=params_knee_constant,
    ndim=1,
    freq_space='linear',
    powers_space='log10',
)


# Collect available aperiodic modes
AP_MODES = {
    'fixed' : ap_powerlaw,
    'knee' : ap_lorentzian,
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
    formula=r'P(F)_n = a * exp (\frac{- (F - c)^2}{2 * w^2})',
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
    formula=r'P(F)_n = a * \frac{2}{w\sqrt{2\pi}} e^{-\frac{(F - \epsilon)^2} {2w^2}} * 0.5 * (1 + erf(s + \frac{F - c}{w\sqrt{2}})',
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
    formula=r'P(F)_n = a * \frac {w^2} {(F - c)^2 + w^2}',
    func=cauchy_function,
    jacobian=None,
    params=params_cauchy,
    ndim=2,
    freq_space='linear',
    powers_space='log10',
)


## PE - Gamma Mode

params_gamma = ParamDefinition(OrderedDict({
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'shape' : 'Shape parameter of the gamma function.',
    'scale' : 'Scale parameter of the gamma function.',
}))

pe_gamma = Mode(
    name='gamma',
    component='periodic',
    description='Fit a gamma peak function.',
    formula=r'P(F)_n = a * \frac{1}{\Gamma (s)\theta^{s}}(F-c)^{s-1}e^{-\frac{F-c}{\theta}}',
    func=gamma_function,
    jacobian=None,
    params=params_gamma,
    ndim=2,
    freq_space='linear',
    powers_space='log10',
)


## PE - Triangle Mode

params_triangle = ParamDefinition(OrderedDict({
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
}))

pe_triangle = Mode(
    name='triangle',
    component='periodic',
    description='Triangle peak fit function.',
    formula=r'\text{tri}(x) = \begin{cases} 1 - |x| & \text{if } |x| < 1 \\ 0 & \text{if } |x| \geq 1 \end{cases}',
    func=triangle_function,
    jacobian=None,
    params=params_triangle,
    ndim=2,
    freq_space='linear',
    powers_space='log10',
)


# Collect available periodic modes
PE_MODES = {
    'gaussian' : pe_gaussian,
    'skewed_gaussian' : pe_skewed_gaussian,
    'cauchy' : pe_cauchy,
    'gamma' : pe_gamma,
    'triangle' : pe_triangle,
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
