"""Define an algorithm settings object and related functionality."""

from collections import namedtuple

###################################################################################################
###################################################################################################

class SettingsValues():
    """Defines a set of algorithm settings values.

    Parameters
    ----------
    names : list of str
        Names of the settings to hold values for.

    Attributes
    ----------
    values : dict of {str : object}
        Settings values.
    """

    __slots__ = ('values',)

    def __init__(self, names):
        """Initialize settings values."""

        self.values = {name : None for name in names}


    def __getattr__(self, name):
        """Allow for accessing settings values as attributes."""

        try:
            return self.values[name]
        except KeyError:
            raise AttributeError(name)


    def __setattr__(self, name, value):
        """Allow for setting settings values as attributes."""

        if name == 'values':
            super().__setattr__(name, value)
        else:
            getattr(self, name)
            self.values[name] = value


    def __getstate__(self):
        """Define how to get object state - for pickling."""

        return self.values


    def __setstate__(self, state):
        """Define how to set object state - for pickling."""

        self.values = state


    @property
    def names(self):
        """Property attribute for settings names."""

        return list(self.values.keys())


    def clear(self):
        """Clear all settings - resetting to None."""

        for setting in self.names:
            self.values[setting] = None


class SettingsDefinition():
    """Defines a set of algorithm settings.

    Parameters
    ----------
    definitions : dict
        Settings definition.
        Each key should be a str name of a setting.
        Each value should be a dictionary with keys 'type' and 'description', with str values.

    Attributes
    ----------
    names : list of str
        Names of the settings defined in the object.
    descriptions : dict of {str : str}
        Description of each setting.
    types : dict of {str : str}
        Type for each setting.
    values : dict of {str : object}
        Value of each setting.
    """

    def __init__(self, definitions):
        """Initialize settings definition."""

        self._definitions = definitions


    def __len__(self):
        """Define the length of the object as the number of settings."""

        return len(self._definitions)


    def _get_definitions_subdict(self, field):
        """Helper function to select from definitions dictionary."""

        return {label : self._definitions[label][field] for label in self._definitions.keys()}


    @property
    def names(self):
        """Make property alias for setting names."""

        return list(self._definitions.keys())


    @property
    def types(self):
        """Make property alias for setting types."""

        return self._get_definitions_subdict('type')


    @property
    def descriptions(self):
        """Make property alias for setting descriptions."""

        return self._get_definitions_subdict('description')


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

            @property
            def names(self):
                return list(self._fields)

        ModelSettings.__doc__ = self.make_docstring()

        return ModelSettings
