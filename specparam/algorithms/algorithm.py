"""Define object to manage algorithm implementations."""

import numpy as np

from specparam.utils.checks import check_input_options
from specparam.algorithms.settings import SettingsDefinition, SettingsValues
from specparam.modutils.docs import docs_get_section, replace_docstring_sections
from specparam.reports.strings import gen_settings_str

###################################################################################################
###################################################################################################

DATA_FORMATS = ['spectrum', 'spectra', 'spectrogram', 'spectrograms']

class Algorithm():
    """Template object for defining a fit algorithm.

    Parameters
    ----------
    name : str
        Name of the fitting algorithm.
    description : str
        Description of the fitting algorithm.
    public_settings : SettingsDefinition or dict
        Name and description of public settings for the fitting algorithm.
    private_settings :  SettingsDefinition or dict, optional
        Name and description of private settings for the fitting algorithm.
    data_format : {'spectrum', 'spectra', 'spectrogram', 'spectrograms'}
        Set base data format the model can be applied to.
    modes : Modes
        Modes object with fit mode definitions.
    data : Data
        Data object with spectral data and metadata.
    results : Results
        Results object with model fit results and metrics.
    debug :  bool
        Whether to run in debug state, raising an error if encountered during fitting.
    """

    def __init__(self, name, description, public_settings, private_settings=None,
                 data_format='spectrum', modes=None, data=None, results=None, debug=False):
        """Initialize Algorithm object."""

        self.name = name
        self.description = description

        if not isinstance(public_settings, SettingsDefinition):
            public_settings = SettingsDefinition(public_settings)
        self.public_settings = public_settings
        self.settings = SettingsValues(self.public_settings.names)

        if private_settings is None:
            private_settings = {}
        if not isinstance(private_settings, SettingsDefinition):
            private_settings = SettingsDefinition(private_settings)
        self.private_settings = private_settings
        self._settings = SettingsValues(self.private_settings.names)

        check_input_options(data_format, DATA_FORMATS, 'data_format')
        self.data_format = data_format

        self.modes = None
        self.data = None
        self.results = None
        self._reset_subobjects(modes, data, results)

        self.set_debug(debug)


    def _fit_prechecks(self, verbose):
        """Pre-checks to run before the fit function - if are some, overload this function."""


    def _fit(self):
        """Required fit function, to be overloaded."""


    def add_settings(self, settings):
        """Add settings into object from a ModelSettings object.

        Parameters
        ----------
        settings : ModelSettings
            A data object containing model settings.
        """

        for setting in settings._fields:
            setattr(self.settings, setting, getattr(settings, setting))


    def get_settings(self):
        """Return user defined settings of the current object.

        Returns
        -------
        ModelSettings
            Object containing the settings from the current object.
        """

        return self.public_settings.make_model_settings()(\
            **{key : getattr(self.settings, key) for key in self.public_settings.names})


    def get_debug(self):
        """Return object debug status."""

        return self._debug


    def set_debug(self, debug):
        """Set debug state, which controls if an error is raised if model fitting is unsuccessful.

        Parameters
        ----------
        debug : bool
            Whether to run in debug state.
        """

        self._debug = debug


    def print(self, description=False, concise=False):
        """Print out the algorithm name and fit settings.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_settings_str(self, description, concise))


    def _reset_subobjects(self, modes=None, data=None, results=None):
        """Reset links to sub-objects (mode / data / results).

        Parameters
        ----------
        modes : Modes
            Model modes object.
        data : Data*
            Model data object.
        results : Results*
            Model results object.
        """

        if modes is not None:
            self.modes = modes
        if data is not None:
            self.data = data
        if results is not None:
            self.results = results


## AlgorithmCF

CURVE_FIT_SETTINGS = SettingsDefinition({
    'maxfev' : {
        'type' : 'int',
        'description' : 'The maximum number of calls to the curve fitting function.',
        },
    'tol' : {
        'type' : 'float',
        'description' : \
            'The tolerance setting for curve fitting (see scipy.curve_fit: ftol / xtol / gtol).'
        },
})

@replace_docstring_sections([docs_get_section(Algorithm.__doc__, 'Parameters')])
class AlgorithmCF(Algorithm):
    """Template object for defining a fit algorithm that uses `curve_fit`.

    Parameters
    ----------
    % copied in from Algorithm
    """

    def __init__(self, name, description, public_settings, private_settings=None,
                 data_format='spectrum', modes=None, data=None, results=None, debug=False):
        """Initialize Algorithm object."""

        Algorithm.__init__(self, name=name, description=description,
                           public_settings=public_settings, private_settings=private_settings,
                           data_format=data_format, modes=modes, data=data, results=results,
                           debug=debug)

        self._cf_settings_desc = CURVE_FIT_SETTINGS
        self._cf_settings = SettingsValues(self._cf_settings_desc.names)


    def _initialize_bounds(self, mode):
        """Initialize a bounds definition.

        Parameters
        ----------
        mode : {'aperiodic', 'periodic'}
            Which mode to initialize for.

        Returns
        -------
        bounds : tuple of array
            Bounds values.

        Notes
        -----
        Output follows the needed bounds definition for curve_fit, which is:
            ([low_bound_param1, low_bound_param2],
             [high_bound_param1, high_bound_param2])
        """

        # If modes defined, get number of params - otherwise set stores as empty
        if self.modes is not None:
            n_params = getattr(self.modes, mode).n_params
        else:
            n_params = 0

        bounds = (np.array([-np.inf] * n_params), np.array([np.inf] * n_params))

        return bounds


    def _initialize_guess(self, mode):
        """Initialize a guess definition.

        Parameters
        ----------
        mode : {'aperiodic', 'periodic'}
            Which mode to initialize for.

        Returns
        -------
        guess : 1d array
            Guess values.
        """

        guess = np.zeros([getattr(self.modes, mode).n_params])

        return guess
