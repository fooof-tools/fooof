"""Define model parameters object."""

import numpy as np

###################################################################################################
###################################################################################################

class ModelParameters():
    """Object to manage model fit parameters.

    Parameters
    ----------
    modes : Modes
        Fit modes defintion.
        If provided, used to initialize parameter arrays to correct sizes.

    Attributes
    ----------
    aperiodic : 1d array
        Aperiodic parameters of the model fit.
    peak : 1d array
        Peak parameters of the model fit.
    gaussian : 1d array
        Gaussian parameters of the model fit.
    """

    def __init__(self, modes=None):
        """Initialize ModelParameters object."""

        self.aperiodic = np.nan
        self.peak = np.nan
        self.gaussian = np.nan

        self.reset(modes)

    def reset(self, modes=None):
        """Reset parameters."""

        # Aperiodic parameters
        if modes:
            self.aperiodic = np.array([np.nan] * modes.aperiodic.n_params)
        else:
            self.aperiodic = np.nan

        # Periodic parameters
        if modes:
            self.gaussian = np.empty([0, modes.periodic.n_params])
            self.peak = np.empty([0, modes.periodic.n_params])
        else:
            self.gaussian = np.nan
            self.peak = np.nan
