"""Define an algorithm settings object and related functionality."""

from collections import namedtuple

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


    def make_model_settings(self):
        """Create a custom ModelSettings object for the current object's settings definition."""

        class ModelSettings(namedtuple('ModelSettings', self.names)):
            __slots__ = ()
        ModelSettings.__doc__ = self.make_docstring()

        return ModelSettings
