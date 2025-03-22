"""Parameter definition for Modes."""

###################################################################################################
###################################################################################################

class ParamDefinition():
    """Defines a parameter definition for a fit mode.

    Parameters
    ----------
    params : OrderedDict
        Parameter information, in which:
            keys should be the name of the parameters
            values should have the description of each parameter
            the order should match the function definition
    """

    def __init__(self, params):
        """Initialize a parameter definition."""

        self.params = params


    @property
    def n_params(self):
        """Define property attribute for the number of parameters."""

        return len(self.params)


    @property
    def labels(self):
        """Define property attribute for parameter labels."""

        return list(self.params.keys())


    @property
    def descriptions(self):
        """Define property attribute for parameter descriptions."""

        return self.params


    @property
    def indices(self):
        """Define property attribute for parameter indices."""

        return {label : index for index, label in enumerate(self.params)}
