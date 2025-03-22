"""Modes object."""

from specparam.utils.checks import check_input_options

###################################################################################################
###################################################################################################

# Set valid options for Mode parameters
VALID_COMPONENTS = ['periodic', 'aperiodic']
VALID_SPACINGS = ['linear', 'log10']


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
    params : ParamDefinition
        Parameter definition.
    freq_space : {'linear', 'log10'}
        Required spacing of the frequency values for this mode.
    powers_space : {'linear', 'log10'}
        Required spacing of the power values for this mode.
    """

    def __init__(self, name, component, description, func, jacobian,
                 params, freq_space, powers_space):
        """Initialize a mode."""

        self.name = name
        self.component = check_input_options(component, VALID_COMPONENTS, 'component')
        self.description = description

        self.func = func
        self.jacobian = jacobian

        self.params = params

        self.spacing = {
            'frequency' : check_input_options(freq_space, VALID_SPACINGS, 'freq_space'),
            'powers' : check_input_options(powers_space, VALID_SPACINGS, 'powers_space'),
        }


    def __repr__(self):
        """Return representation of this object as the name."""

        return 'MODE: ' + self.component + '-' + self.name


    def __eq__(self, other):
        """Define equality comparison between objects as equivalent dictionary representations.

        Parameters
        ----------
        other : Mode
            Other Mode object to compare to.
        """

        return self.__dict__ == other.__dict__


    @property
    def n_params(self):
        """Define property attribute to access the number of parameters."""

        return self.params.n_params
