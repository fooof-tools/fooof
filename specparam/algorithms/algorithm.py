"""Define original spectral fitting algorithm object."""

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


    def _fit():
        """Required fit function, to be overloaded."""
        pass
