"""Define fitting modes."""

from specparam.core.funcs import *

###################################################################################################
## MODES OUTLINE

class Mode():
    """Defines a fit mode.

    Parameters
    ----------
    name : str
        Name of the mode.
    component : {'periodic', 'aperiodic'},
        Which component the mode relates to.
    description : str
        Description of the mode.
    func : callable
        Function that defines the fit function for the mode.
    params : list of str
        Name of output parameter(s).
    param_description : dict
        Descriptions of the parameters.
        Should have same length and keys as `params`.
    freq_space : {'linear', 'log10'}
        Required spacing of the frequency values for this mode.
    powers_space : {'linear', 'log10'}
        Required spacing of the power values for this mode.
    """

    def __init__(self, name, component, description, func, params, param_description,
                 freq_space, powers_space):
        """Initialize a mode."""

        self.name = name
        self.component = component
        self.description = description
        self.func = func
        self.params = params
        self.param_description = param_description
        self.freq_space = freq_space
        self.powers_space = powers_space


    def __repr__(self):
        """Return representation of this object as the name."""

        return self.name


    @property
    def n_params(self):
        """Define property attribute for the number of parameters."""

        return len(self.params)


    @property
    def param_indices(self):
        """Define property attribute for the indices of the parameters."""

        return {label : index for index, label in enumerate(self.params)}

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
