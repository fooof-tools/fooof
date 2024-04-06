"""Define base fit objects."""

from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np

from specparam.core.utils import unlog
from specparam.core.funcs import infer_ap_func
from specparam.core.utils import check_array_dim
from specparam.data import FitResults, ModelSettings
from specparam.core.items import OBJ_DESC
from specparam.core.modutils import safe_import

###################################################################################################
###################################################################################################

class BaseFit():
    """Define BaseFit object."""
    # pylint: disable=attribute-defined-outside-init, arguments-differ

    def __init__(self, aperiodic_mode, periodic_mode, debug_mode=False,
                 verbose=True, error_metric='MAE'):

        # Set fit component modes
        self.aperiodic_mode = aperiodic_mode
        self.periodic_mode = periodic_mode

        # Set run modes
        self.set_debug_mode(debug_mode)
        self.verbose = verbose

        # Initialize results attributes
        self._reset_results(True)

        # Set private run settings
        self._error_metric = error_metric


    @property
    def has_model(self):
        """Indicator for if the object contains a model fit.

        Notes
        -----
        This check uses the aperiodic params, which are:

        - nan if no model has been fit
        - necessarily defined, as floats, if model has been fit
        """

        return True if not np.all(np.isnan(self.aperiodic_params_)) else False


    @property
    def n_peaks_(self):
        """How many peaks were fit in the model."""

        return self.peak_params_.shape[0] if self.has_model else None


    def fit(self, freqs=None, power_spectrum=None, freq_range=None):
        """Fit a power spectrum as a combination of periodic and aperiodic components.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array, optional
            Power values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to.
            If not provided, keeps the entire range.

        Raises
        ------
        NoDataError
            If no data is available to fit.
        FitError
            If model fitting fails to fit. Only raised in debug mode.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        return self._fit(freqs=freqs, power_spectrum=power_spectrum, freq_range=freq_range)


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


    def add_results(self, results):
        """Add results data into object from a FitResults object.

        Parameters
        ----------
        results : FitResults
            A data object containing the results from fitting a power spectrum model.
        """

        self.aperiodic_params_ = results.aperiodic_params
        self.gaussian_params_ = results.gaussian_params
        self.peak_params_ = results.peak_params
        self.r_squared_ = results.r_squared
        self.error_ = results.error

        self._check_loaded_results(results._asdict())


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics.

        Returns
        -------
        FitResults
            Object containing the model fit results from the current object.
        """

        return FitResults(**{key.strip('_') : getattr(self, key) \
            for key in OBJ_DESC['results']})


    def get_model(self, component='full', space='log'):
        """Get a model component.

        Parameters
        ----------
        component : {'full', 'aperiodic', 'peak'}
            Which model component to return.
                'full' - full model
                'aperiodic' - isolated aperiodic model component
                'peak' - isolated peak model component
        space : {'log', 'linear'}
            Which space to return the model component in.
                'log' - returns in log10 space.
                'linear' - returns in linear space.

        Returns
        -------
        output : 1d array
            Specified model component, in specified spacing.

        Notes
        -----
        The 'space' parameter doesn't just define the spacing of the model component
        values, but rather defines the space of the additive model such that
        `model = aperiodic_component + peak_component`.
        With space set as 'log', this combination holds in log space.
        With space set as 'linear', this combination holds in linear space.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.modeled_spectrum_ if space == 'log' else unlog(self.modeled_spectrum_)
        elif component == 'aperiodic':
            output = self._ap_fit if space == 'log' else unlog(self._ap_fit)
        elif component == 'peak':
            output = self._peak_fit if space == 'log' else \
                unlog(self.modeled_spectrum_) - unlog(self._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output


    def set_debug_mode(self, debug):
        """Set debug mode, which controls if an error is raised if model fitting is unsuccessful.

        Parameters
        ----------
        debug : bool
            Whether to run in debug mode.
        """

        self._debug = debug


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

            # If aperiodic params available, infer whether knee fitting was used,
            if not np.all(np.isnan(self.aperiodic_params_)):
                self.aperiodic_mode = infer_ap_func(self.aperiodic_params_)

        # Reset internal settings so that they are consistent with what was loaded
        #   Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _check_loaded_results(self, data):
        """Check if results have been added and check data.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If results loaded, check dimensions of peak parameters
        #   This fixes an issue where they end up the wrong shape if they are empty (no peaks)
        if set(OBJ_DESC['results']).issubset(set(data.keys())):
            self.peak_params_ = check_array_dim(self.peak_params_)
            self.gaussian_params_ = check_array_dim(self.gaussian_params_)


    def _reset_internal_settings(self):
        """"Can be overloaded if any resetting needed for internal settings."""


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

            # Data components
            self._spectrum_flat = None
            self._spectrum_peak_rm = None

            # Modeled spectrum components
            self.modeled_spectrum_ = None
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


class BaseFit2D(BaseFit):

    def __init__(self, aperiodic_mode, periodic_mode, debug_mode=False, verbose=True):

        BaseFit.__init__(self, aperiodic_mode, periodic_mode, debug_mode=False, verbose=True)

        self._reset_group_results()


    def __len__(self):
        """Define the length of the object as the number of model fit results available."""

        return len(self.group_results)


    def __iter__(self):
        """Allow for iterating across the object by stepping across model fit results."""

        for result in self.group_results:
            yield result


    def __getitem__(self, index):
        """Allow for indexing into the object to select model fit results."""

        return self.group_results[index]


    def _reset_group_results(self, length=0):
        """Set, or reset, results to be empty.

        Parameters
        ----------
        length : int, optional, default: 0
            Length of list of empty lists to initialize. If 0, creates a single empty list.
        """

        self.group_results = [[]] * length


    @property
    def has_model(self):
        """Indicator for if the object contains model fits."""

        return True if self.group_results else False


    @property
    def n_peaks_(self):
        """How many peaks were fit for each model."""

        return [res.peak_params.shape[0] for res in self] if self.has_model else None


    @property
    def n_null_(self):
        """How many model fits are null."""

        return sum([1 for res in self.group_results if np.isnan(res.aperiodic_params[0])]) \
            if self.has_model else None


    @property
    def null_inds_(self):
        """The indices for model fits that are null."""

        return [ind for ind, res in enumerate(self.group_results) \
            if np.isnan(res.aperiodic_params[0])] \
            if self.has_model else None


    def add_results(self, results):
        """Add results data into object from a FitResults object.

        Parameters
        ----------
        results : list of FitResults
            List of data object containing the results from fitting a power spectrum models.
        """

        self.group_results = results


    def get_results(self):
        """Return the results run across a group of power spectra."""

        return self.group_results


    def _get_results(self):
        """Create an alias to SpectralModel.get_results for the group object, for internal use."""

        return super().get_results()


    def fit(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1, progress=None):
        """Fit a group of power spectra.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to fit the model to. If not provided, fits the entire given range.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If freqs & power spectra provided together, add data to object
        if freqs is not None and power_spectra is not None:
            self.add_data(freqs, power_spectra, freq_range)

        # If 'verbose', print out a marker of what is being run
        if self.verbose and not progress:
            print('Fitting model across {} power spectra.'.format(len(self.power_spectra)))

        # Run linearly
        if n_jobs == 1:
            self._reset_group_results(len(self.power_spectra))
            for ind, power_spectrum in \
                _progress(enumerate(self.power_spectra), progress, len(self)):
                self._fit(power_spectrum=power_spectrum)
                self.group_results[ind] = self._get_results()

        # Run in parallel
        else:
            self._reset_group_results()
            n_jobs = cpu_count() if n_jobs == -1 else n_jobs
            with Pool(processes=n_jobs) as pool:
                self.group_results = list(_progress(pool.imap(partial(_par_fit, group=self),
                                                              self.power_spectra),
                                                    progress, len(self.power_spectra)))

        # Clear the individual power spectrum and fit results of the current fit
        self._reset_data_results(clear_spectrum=True, clear_results=True)

###################################################################################################
## Helper functions for running fitting in parallel

def _par_fit(power_spectrum, group):
    """Helper function for running in parallel."""

    group._fit(power_spectrum=power_spectrum)

    return group._get_results()


def _progress(iterable, progress, n_to_run):
    """Add a progress bar to an iterable to be processed.

    Parameters
    ----------
    iterable : list or iterable
        Iterable object to potentially apply progress tracking to.
    progress : {None, 'tqdm', 'tqdm.notebook'}
        Which kind of progress bar to use. If None, no progress bar is used.
    n_to_run : int
        Number of jobs to complete.

    Returns
    -------
    pbar : iterable or tqdm object
        Iterable object, with tqdm progress functionality, if requested.

    Raises
    ------
    ValueError
        If the input for `progress` is not understood.

    Notes
    -----
    The explicit `n_to_run` input is required as tqdm requires this in the parallel case.
    The `tqdm` object that is potentially returned acts the same as the underlying iterable,
    with the addition of printing out progress every time items are requested.
    """

    # Check progress specifier is okay
    tqdm_options = ['tqdm', 'tqdm.notebook']
    if progress is not None and progress not in tqdm_options:
        raise ValueError("Progress bar option not understood.")

    # Set the display text for the progress bar
    pbar_desc = 'Running group fits.'

    # Use a tqdm, progress bar, if requested
    if progress:

        # Try loading the tqdm module
        tqdm = safe_import(progress)

        if not tqdm:

            # If tqdm isn't available, proceed without a progress bar
            print(("A progress bar requiring the 'tqdm' module was requested, "
                   "but 'tqdm' is not installed. \nProceeding without using a progress bar."))
            pbar = iterable

        else:

            # If tqdm loaded, apply the progress bar to the iterable
            pbar = tqdm.tqdm(iterable, desc=pbar_desc, total=n_to_run, dynamic_ncols=True)

    # If progress is None, return the original iterable without a progress bar applied
    else:
        pbar = iterable

    return pbar
