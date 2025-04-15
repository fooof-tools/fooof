"""Define object to manage algorithm implementations."""

from specparam.utils.checks import check_input_options
from specparam.algorithms.settings import SettingsDefinition, SettingsValues

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


    def _fit_prechecks(self):
        """Pre-checks to run before the fit function - if are some, overload this function."""


    def _fit(self):
        """Required fit function, to be overloaded."""


    def add_settings(self, settings):
        """Add settings into object from a ModelSettings object.

        Parameters
        ----------
        settings : ModelSettings
            A data object containing the settings for a power spectrum model.
        """

        for setting in settings._fields:
            setattr(self.settings, setting, getattr(settings, setting))

        self._check_loaded_settings(settings._asdict())


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


    def _check_loaded_settings(self, data):
        """Check if settings added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If settings not loaded from file, clear from object, so that default
        # settings, which are potentially wrong for loaded data, aren't kept
        if not set(self.settings.names).issubset(set(data.keys())):

            # Reset all public settings to None
            for setting in self.settings.names:
                setattr(self.settings, setting, None)

        # Reset internal settings so that they are consistent with what was loaded
        #   Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _reset_internal_settings(self):
        """"Can be overloaded if any resetting needed for internal settings."""


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
