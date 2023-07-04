"""Time model object and associated code for fitting the model to spectra across time."""

from specparam.objs import SpectralGroupModel

###################################################################################################
###################################################################################################

class SpectralTimeModel(SpectralGroupModel):
    """xxx"""

    def __init__(self, *args, **kwargs):
        """Initialize object with desired settings."""

        SpectralGroupModel.__init__(self, *args, **kwargs)
