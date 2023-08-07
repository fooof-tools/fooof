"""   """

from specparam.core.funcs import *

###################################################################################################
## MODES OUTLINE

class Mode():

    def __init__(self, name, component, description, func, params, param_description,
                 freq_space, powers_space):

        self.name = name
        self.component = component
        self.description = description
        self.func = func
        self.params = params
        self.param_description = param_description
        self.freq_space = freq_space
        self.powers_space = powers_space

    def __repr__(self):
        return self.name

###################################################################################################
## APERIODIC MODES

# 'Fixed' model
# ap_fixed = {
#     'name' : 'fixed',
#     'component' : 'aperiodic',
#     'description' : 'Fit an exponential, with no knee.',
#     'func' : expo_nk_function,
#     'params' : ['offset', 'exponent'],
#     'param_description' : {
#         'offset' : 'Offset of the aperiodic component.',
#         'exponent' : 'Exponent of the aperiodic component.'
#     },
#     'freq_space' : 'linear',
#     'powers_space' : 'log10',
# }

param_desc_fixed = {
    'offset' : 'Offset of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}
ap_fixed = Mode('fixed', 'aperiodic', 'Fit an exponential, with no knee.',
                expo_nk_function, ['offset', 'exponent'], param_desc_fixed,
                'linear', 'log10')


# 'Knee' model
# ap_knee = {
#     'name' : 'knee',
#     'component' : 'aperiodic',
#     'description' : 'Fit an exponential, with a knee.',
#     'func' : expo_function,
#     'params' : ['offset', 'knee', 'exponent'],
#     'param_description' : {
#         'offset' : 'Offset of the aperiodic component.',
#         'knee' : 'Knee of the aperiodic component.',
#         'exponent' : 'Exponent of the aperiodic component.'
#     },
#     'freq_space' : 'linear',
#     'powers_space' : 'log10',
# }


param_desc_knee = {
    'offset' : 'Offset of the aperiodic component.',
    'knee' : 'Knee of the aperiodic component.',
    'exponent' : 'Exponent of the aperiodic component.',
}

ap_knee = Mode('knee', 'aperiodic', 'Fit an exponential, with a knee.',
               expo_function, ['offset', 'knee', 'exponent'], param_desc_knee,
               'linear', 'log10')

# Collect available aperiodic modes
AP_MODES = {
    'fixed' : ap_fixed,
    'knee' : ap_knee,
}

###################################################################################################
## PERIODIC MODES

# # 'Gaussian' model
# pe_gaussian = {
#     'name' : 'gaussian',
#     'component' : 'periodic',
#     'description' : 'Gaussian peak fit function.',
#     'func' : gaussian_function,
#     'params' : ['cf', 'pw', 'bw'],
#     'param_description' : {
#         'cf' : 'Center frequency of the peak.',
#         'pw' : 'Power of the peak, over and above the aperiodic component.',
#         'bw' : 'Bandwidth of the peak.',
#     },
#     'freq_space' : 'linear',
#     'powers_space' : 'log10',
# }

param_desc_gaus = {
    'cf' : 'Center frequency of the peak.',
    'pw' : 'Power of the peak, over and above the aperiodic component.',
    'bw' : 'Bandwidth of the peak.',
}

pe_gaussian = Mode('gaussian', 'periodic', 'Gaussian peak fit function.',
                   gaussian_function, ['cf', 'pw', 'bw'], param_desc_gaus,
                   'linear', 'log10')

# Collect available periodic modes
PE_MODES = {
    'gaussian' : pe_gaussian,
}
