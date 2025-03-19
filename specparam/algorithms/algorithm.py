"""Define original spectral fitting algorithm object."""

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
    settings : dict
        Name and description of settings for the fitting algorithm.
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
