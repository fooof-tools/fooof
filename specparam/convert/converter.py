"""Parameter converter objects."""

###################################################################################################
###################################################################################################

class BaseParamConverter():
    """General class for parameter converters - to be inherited by component specific converter.

    Parameters
    ----------
    component : {'aperiodic', 'periodic'},
        Which component the converter relates to.
    parameter : str
        Label of the parameter the converter is for.
    name : str
        Name of the parameter converter.
    description : str
        Description of the parameter converter.
    function : callable
        Function that implements the parameter conversion.
    """

    def __init__(self, component, parameter, name, description, function):
        """Initialize a parameter converter."""

        self.component = component
        self.parameter = parameter
        self.name = name
        self.description = description
        self.function = function


class AperiodicParamConverter(BaseParamConverter):
    """Parameter converter for aperiodic parameters."""

    def __init__(self, parameter, name, description, function):
        """Initialize an aperiodic parameter converter."""

        super().__init__('aperiodic', parameter, name, description, function)


    def __call__(self, fit_value, model):
        """Call the aperiodic parameter converter.

        Parameters
        ----------
        fit_value : float
            Fit value for the parameter.
        model : SpectralModel
            Model object.
        """

        return self.function(fit_value, model)


class PeriodicParamConverter(BaseParamConverter):
    """Parameter converter for periodic parameters."""

    def __init__(self, parameter, name, description, function):
        """Initialize a periodic parameter converter."""

        super().__init__('periodic', parameter, name, description, function)


    def __call__(self, fit_value, model, peak_ind):
        """Call the peak parameter converter.

        Parameters
        ----------
        fit_value : float
            Fit value for the parameter.
        model : SpectralModel
            Model object.
        peak_ind : int
            Index of the current peak.
        """

        return self.function(fit_value, model, peak_ind)
