"""Define base fit model object."""

import numpy as np

###################################################################################################
###################################################################################################

class BaseFit():
    """   """

    def __init__(self, aperiodic_mode, periodic_mode, debug_mode=False, verbose=True):

        self.aperiodic_mode = aperiodic_mode
        self.periodic_mode = periodic_mode
        self.set_debug_mode(debug_mode)
        self.verbose = verbose


    def fit(self):
        raise NotImplementedError('The method needs to overloaded with a fit procedure!')


    def set_debug_mode(self, debug):
        """Set debug mode, which controls if an error is raised if model fitting is unsuccessful.

        Parameters
        ----------
        debug : bool
            Whether to run in debug mode.
        """

        self._debug = debug


    def _reset_results(self, clear_results=False):
        """Set, or reset, results attributes to empty.

        Parameters
        ----------
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        if clear_results:

            # Aperiodic parameers
            self.aperiodic_params_ = np.nan

            # Periodic parameters
            self.gaussian_params_ = np.nan
            self.peak_params_ = np.nan

            # Note - for ap / pe params, move to something like `xx_params` and `_xx_params`

            # Goodness of fit measures
            self.r_squared_ = np.nan
            self.error_ = np.nan
            # Note: move to `self.gof` or similar

            # Modeled spectrum components
            self.modeled_spectrum_ = None
            self._spectrum_flat = None
            self._spectrum_peak_rm = None
            self._ap_fit = None
            self._peak_fit = None


    def _calc_r_squared(self):
        """Calculate the r-squared goodness of fit of the model, compared to the original data."""

        r_val = np.corrcoef(self.power_spectrum, self.modeled_spectrum_)
        self.r_squared_ = r_val[0][1] ** 2


    def _calc_error(self, metric=None):
        """Calculate the overall error of the model fit, compared to the original data.

        Parameters
        ----------
        metric : {'MAE', 'MSE', 'RMSE'}, optional
            Which error measure to calculate:
            * 'MAE' : mean absolute error
            * 'MSE' : mean squared error
            * 'RMSE' : root mean squared error

        Raises
        ------
        ValueError
            If the requested error metric is not understood.

        Notes
        -----
        Which measure is applied is by default controlled by the `_error_metric` attribute.
        """

        # If metric is not specified, use the default approach
        metric = self._error_metric if not metric else metric

        if metric == 'MAE':
            self.error_ = np.abs(self.power_spectrum - self.modeled_spectrum_).mean()

        elif metric == 'MSE':
            self.error_ = ((self.power_spectrum - self.modeled_spectrum_) ** 2).mean()

        elif metric == 'RMSE':
            self.error_ = np.sqrt(((self.power_spectrum - self.modeled_spectrum_) ** 2).mean())

        else:
            error_msg = "Error metric '{}' not understood or not implemented.".format(metric)
            raise ValueError(error_msg)
