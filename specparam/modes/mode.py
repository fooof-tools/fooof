"""Mode object."""

from specparam.modes.params import ParamDefinition
from specparam.reports.strings import gen_mode_str
from specparam.utils.checks import check_input_options

###################################################################################################
###################################################################################################

# Set valid options for Mode parameters
VALID_COMPONENTS = ['aperiodic', 'periodic']
VALID_SPACINGS = ['linear', 'log10']


class Mode():
    """Defines a fit mode.

    Parameters
    ----------
    name : str
        Name of the mode.
    component : {'aperiodic', 'periodic'},
        Which component the mode relates to.
    description : str
        Description of the mode.
    formula : str
        Formula of the fit mode.
    func : callable
        Function that defines the fit function for the mode.
    jacobian : callable, optional
        Function for computing Jacobian matrix corresponding to `func`.
    params : dict or ParamDefinition
        Parameter definition.
    ndim : {1, 2}
        Dimensionality of the parameters.
        This reflects whether they require a 1d or 2d array to store.
    freq_space : {'linear', 'log10'}
        Required spacing of the frequency values for this mode.
    powers_space : {'linear', 'log10'}
        Required spacing of the power values for this mode.
    """

    def __init__(self, name, component, description, formula, func,
                 jacobian, params, ndim, freq_space, powers_space):
        """Initialize a mode."""

        self.name = name
        self.component = check_input_options(component, VALID_COMPONENTS, 'component')
        self.description = description
        self.formula = formula

        self.func = func
        self.jacobian = jacobian

        if isinstance(params, dict):
            params = ParamDefinition(params)
        self.params = params

        self.ndim = ndim

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


    def print(self, info='all', description=False, concise=False):
        """Print out current mode.

        Parameters
        ----------
        info : {'all', 'mode', 'params'}
            Which information to print:
                'all': print all information on the mode
                'mode': print information on the mode
                'params': print information on the parameters of the mode
        description : bool, optional, default: False
            Whether to print out a description with current mode.
        concise : bool, optional, default: False
            Whether to print a concise version of the report.
        """

        print(gen_mode_str(self, info, description, concise))
