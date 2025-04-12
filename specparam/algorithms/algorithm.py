"""Define object to manage algorithm implementations."""

from specparam.utils.checks import check_input_options
from specparam.algorithms.settings import SettingsDefinition

###################################################################################################
###################################################################################################

FORMATS = ['spectrum', 'spectra', 'spectrogram', 'spectrograms']


class Algorithm():
    """Template object for defining a fit algorithm.

    Parameters
    ----------
    name : str
        Name of the fitting algorithm.
    description : str
        Description of the fitting algorithm.
    settings : dict
        Name and description of settings for the fitting algorithm.
    format : {'spectrum', 'spectra', 'spectrogram', 'spectrograms'}
        Set base format of data model can be applied to.
    """

    def __init__(self, name, description, settings, format,
                 modes=None, data=None, results=None, debug=False):
        """Initialize Algorithm object."""

        self.name = name
        self.description = description

        if not isinstance(settings, SettingsDefinition):
            settings = SettingsDefinition(settings)
        self.settings = settings

        check_input_options(format, FORMATS, 'format')
        self.format = format

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
            setattr(self, setting, getattr(settings, setting))

        self._check_loaded_settings(settings._asdict())


    def get_settings(self):
        """Return user defined settings of the current object.

        Returns
        -------
        ModelSettings
            Object containing the settings from the current object.
        """

        return self.settings.make_model_settings()(\
            **{key : getattr(self, key) for key in self.settings.names})


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
                setattr(self, setting, None)

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
