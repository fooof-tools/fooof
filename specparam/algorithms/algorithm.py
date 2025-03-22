"""Define original spectral fitting algorithm object."""

from specparam.modes.items import OBJ_DESC
from specparam.data import ModelSettings

###################################################################################################
###################################################################################################

class SettingsDefinition():
    """Defines a set of algorithm settings.

    Parameters
    ----------
    settings : dict
        Settings definition.
        Each key should be a str name of a setting.
        Each value should be a dictionary with keys 'type' and 'description', with str values.
    """

    def __init__(self, settings):
        """Initialize settings definition."""

        self._settings = settings


    def _get_settings_subdict(self, field):
        """Helper function to select from settings dictionary."""

        return {label : self._settings[label][field] for label in self._settings.keys()}


    @property
    def names(self):
        """Make property alias for setting names."""

        return list(self._settings.keys())


    @property
    def types(self):
        """Make property alias for setting types."""

        return self._get_settings_subdict('type')


    @property
    def descriptions(self):
        """Make property alias for setting descriptions."""

        return self._get_settings_subdict('description')


    def make_setting_str(self, name):
        """Make a setting docstring string.

        Parameters
        ----------
        name : str
            Setting name to make string for.

        Returns
        -------
        str
            Setting docstring string.
        """

        setting_str = '' + \
            '    ' + name + ' : ' + self.types[name] + '\n' \
            '        ' + self.descriptions[name]

        return setting_str


    def make_docstring(self):
        """Make docstring for all settings.

        Returns
        -------
        str
            Docstring for all settings.
        """

        pieces = [self.make_setting_str(name) for name in self.names]
        pieces = ['    Parameters', '    ----------'] + pieces
        docstring = '\n'.join(pieces)

        return docstring


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

    def __init__(self, name, description, settings):
        """Initialize Algorithm object."""

        self.algorithm = AlgorithmDefinition(name, description, settings)


    def _fit_prechecks():
        """Prechecks to run before the fit function - if are some, overload this function."""
        pass


    def _fit():
        """Required fit function, to be overloaded."""
        pass


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
