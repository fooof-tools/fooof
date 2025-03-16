"""Modes object."""

###################################################################################################
###################################################################################################

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
    jacobian : callable, optional
        Function for computing Jacobian matrix corresponding to `func`.
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

    def __init__(self, name, component, description, func, jacobian,
                 params, param_description, freq_space, powers_space):
        """Initialize a mode."""

        self.name = name
        self.component = component
        self.description = description

        self.func = func
        self.jacobian = jacobian

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
