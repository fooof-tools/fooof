"""Define object to manage algoirthm implementations."""

from specparam.data import ModelSettings
from specparam.modes.items import OBJ_DESC

###################################################################################################
###################################################################################################

class AlgorithmDefinition():
    """Defines an algorithm definition description.

    Parameters
    ----------
    name : str
        Name of the fitting algorithm.
    description : str
        Description of the fitting algorithm.
    settings : SettingsDefinition
        Definition of settings for the fitting algorithm.
    """

    def __init__(self, name, description, settings):
        """Initialize AlgorithmDefinition object."""

        self.name = name
        self.description = description
        self.settings = settings


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

    Attributes
    ----------
    algorithm : AlgorithmDefinition
        Algorithm information.
    """

    def __init__(self, name, description, settings, debug=False):
        """Initialize Algorithm object."""

        self.algorithm = AlgorithmDefinition(name, description, settings)

        self.set_debug(debug)


    def _fit_prechecks(self):
        """Prechecks to run before the fit function - if are some, overload this function."""


    def _fit(self):
        """Required fit function, to be overloaded."""


    def add_settings(self, settings):
        """Add settings into object from a ModelSettings object.

        Parameters
        ----------
        settings : ModelSettings
            A data object containing the settings for a power spectrum model.
        """

        for setting in OBJ_DESC['settings']:
            setattr(self, setting, getattr(settings, setting))

        self._check_loaded_settings(settings._asdict())


    def get_settings(self):
        """Return user defined settings of the current object.

        Returns
        -------
        ModelSettings
            Object containing the settings from the current object.
        """

        return ModelSettings(**{key : getattr(self, key) \
                             for key in OBJ_DESC['settings']})


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
        if not set(OBJ_DESC['settings']).issubset(set(data.keys())):

            # Reset all public settings to None
            for setting in OBJ_DESC['settings']:
                setattr(self, setting, None)

        # Reset internal settings so that they are consistent with what was loaded
        #   Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _reset_internal_settings(self):
        """"Can be overloaded if any resetting needed for internal settings."""
