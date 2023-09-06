"""ERPparam Object - base object which defines the model.

Private Attributes
==================
Private attributes of the ERPparam object are documented here.

Data Attributes
---------------

Model Component Attributes
--------------------------
_peak_fit : 1d array
    Values of the isolated peak fit.

Internal Settings Attributes
----------------------------
_cf_bound : float
    Parameter bounds for peak time when fitting gaussians.
_bw_std_edge : float
    Bandwidth threshold for edge rejection of peaks, in units of gaussian standard deviation.
_gauss_overlap_thresh : float
    Degree of overlap (in units of standard deviation) between gaussian guesses to drop one.
_gauss_std_limits : list of [float, float]
    Peak width limits, converted to use for gaussian standard deviation parameter.
    This attribute is computed based on `peak_width_limits` and should not be updated directly.
_maxfev : int
    The maximum number of calls to the curve fitting function.
_error_metric : str
    The error metric to use for post-hoc measures of model fit error.

Run Modes
---------
_debug : bool
    Whether the object is set in debug mode.
    This should be controlled by using the `set_debug_mode` method.
_check_data : bool
    Whether to check added data for NaN or Inf values, and fail out if present.
    This should be controlled by using the `set_check_data_mode` method.

Code Notes
----------
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

import warnings
from copy import deepcopy

import numpy as np
from numpy.linalg import LinAlgError
from scipy.optimize import curve_fit

from ERPparam.core.items import OBJ_DESC
from ERPparam.core.info import get_indices
from ERPparam.core.io import save_fm, load_json
from ERPparam.core.reports import save_report_fm
from ERPparam.core.modutils import copy_doc_func_to_method
from ERPparam.core.utils import group_three, check_array_dim
from ERPparam.core.funcs import gaussian_function
from ERPparam.core.errors import (FitError, NoModelError, DataError,
                               NoDataError, InconsistentDataError)
from ERPparam.core.strings import (gen_settings_str, gen_results_fm_str,
                                gen_issue_str, gen_width_warning_str)

from ERPparam.plts.model import plot_ERPparam
from ERPparam.utils.data import trim_spectrum
from ERPparam.utils.params import compute_gauss_std
from ERPparam.data import ERPparamResults, ERPparamSettings, ERPparamMetaData
from ERPparam.data.conversions import model_to_dataframe
from ERPparam.sim.gen import gen_time_vector, gen_periodic

###################################################################################################
###################################################################################################

class ERPparam():
    """Model an event-related potential (ERP) as a combination of periodic components (Gaussian peaks).

    Parameters
    ----------
    peak_width_limits : tuple of (float, float), optional, default: (0.5, 12.0)
        Limits on possible peak width, in Hz, as (lower_bound, upper_bound).
    max_n_peaks : int, optional, default: inf
        Maximum number of peaks to fit.
    min_peak_height : float, optional, default: 0
        Absolute threshold for detecting peaks.
        This threshold is defined in absolute units of the signal (log power).
    peak_threshold : float, optional, default: 2.0
        Relative threshold for detecting peaks.
        This threshold is defined in relative units of the signal (standard deviation).
    verbose : bool, optional, default: True
        Verbosity mode. If True, prints out warnings and general status updates.

    Attributes
    ----------
    time : 1d array
        Time vector for the signal.
    signal : 1d array
        Evoked response, voltage values.
    time_range : list of [float, float]
        Time range of the signal to be fit, as [earliest_time, latest_time].
    fs : float
        Sampling frequency.
    peak_params_ : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CT, PW, BW].
    gaussian_params_ : 2d array
        Parameters that define the gaussian fit(s).
        Each row is a gaussian, as [mean, height, standard deviation].
    shape_params_ : 2d array
        ERP shape parameters for each peak.
        Each row is a peak, as [duration, rise-time, decay-time, rise-decay symmetry,
        FWHM, rising sharpness, decaying sharpness].
    r_squared_ : float
        R-squared of the fit between the input signal and the full model fit.
    error_ : float
        Error of the full model fit.
    n_peaks_ : int
        The number of peaks fit in the model.
    has_data : bool
        Whether data is loaded to the object.
    has_model : bool
        Whether model results are available in the object.

    Notes
    -----
    - Commonly used abbreviations used in this module include:
      CT: peak time, PW: power, BW: Bandwidth
    - Input signal must be provided.
    - Input signals should be smooth, as overly noisy signals may lead to bad fits.
    - The gaussian params are those that define the gaussian of the fit, where as the peak
      params are a modified version, in which the CT of the peak is the mean of the gaussian,
      the PW of the peak is the height of the gaussian, and the BW of the peak, is 2*std of the 
      gaussian (as 'two sided' bandwidth).
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, signal=None, time=None, time_range=None, peak_width_limits=(0.5, 12.0), max_n_peaks=np.inf, 
                 peak_threshold=2.0, min_peak_height=0.0, verbose=True):
        
        self.peak_width_limits = peak_width_limits
        self.max_n_peaks = max_n_peaks
        self.min_peak_height = min_peak_height
        self.peak_threshold = peak_threshold
        self.verbose = verbose
        # print('...')
        # print(peak_width_limits)
        # print(max_n_peaks)
        # print('...')

        # Threshold for how far a peak has to be from edge to keep.
        #   This is defined in units of gaussian standard deviation
        self._bw_std_edge = 1.0
        # Degree of overlap between gaussians for one to be dropped
        #   This is defined in units of gaussian standard deviation
        self._gauss_overlap_thresh = 0.75
        # Parameter bounds for center when fitting gaussians, in terms of +/- std dev
        self._cf_bound = 1.5
        # The maximum number of calls to the curve fitting function
        self._maxfev = 500
        # The error metric to calculate, post model fitting. See `_calc_error` for options
        #   Note: this is for checking error post fitting, not an objective function for fitting
        self._error_metric = 'MAE'

        ## RUN MODES
        # Set default debug mode - controls if an error is raised if model fitting is unsuccessful
        self._debug = False
        # Set default data checking modes - controls which checks get run on input data
        #   check_times: check the frequency values, and raises an error for uneven spacing
        self._check_times = True
        #   check_data: checks the power values and raises an error for any NaN / Inf values
        self._check_data = True

        # Set internal settings, based on inputs, and initialize data & results attributes
        self._reset_internal_settings()
        self._reset_data_results(True, True, True)

        # If user inputs data upon initialization, then populate these, but AFTER we've run _reset_data_results()
        if time is not None and signal is not None:
            self.add_data(time, signal, time_range)


    @property
    def has_data(self):
        """Indicator for if the object contains data."""

        return True if (np.any(self.signal) and np.any(self.time)) else False


    @property
    def has_model(self):
        """Indicator for if the object contains a model fit.

        Notes
        -----
        This check uses the Gaussian params, which are:

        - nan if no model has been fit
        - necessarily defined, as floats, if model has been fit
        """

        return True if not np.all(np.isnan(self.gaussian_params_)) else False


    @property
    def n_peaks_(self):
        """How many peaks were fit in the model."""

        return self.peak_params_.shape[0] if self.has_model else None


    def _reset_internal_settings(self):
        """Set, or reset, internal settings, based on what is provided in init.

        Notes
        -----
        These settings are for internal use, based on what is provided to, or set in `__init__`.
        They should not be altered by the user.
        """

        # Only update these settings if other relevant settings are available
        if self.peak_width_limits:

            # Bandwidth limits are given in 2-sided peak bandwidth
            #   Convert to gaussian std parameter limits
            self._gauss_std_limits = tuple(bwl / 2 for bwl in self.peak_width_limits)

        # Otherwise, assume settings are unknown (have been cleared) and set to None
        else:
            self._gauss_std_limits = None


    def _reset_data_results(self, clear_time=False, clear_signal=False, clear_results=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_time : bool, optional, default: False
            Whether to clear tike attributes.
        clear_signal : bool, optional, default: False
            Whether to clear signal attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        if clear_time:
            self.time = None
            self.fs = None

        if clear_signal:
            self.signal = None

        if clear_results:

            self.gaussian_params_ = np.ones([0,3])*np.nan
            self.peak_params_ = np.ones([0,3])*np.nan
            self.shape_params_ = np.ones([0,7])*np.nan
            self.r_squared_ = np.nan
            self.error_ = np.nan

            self._peak_fit = None


    def add_data(self, time, signal, time_range=None, clear_results=True):
        """Add data (time, and signal values) to the current object.

        Parameters
        ----------
        time : 1d array, optional
            Time values for the signal.
        signal : 1d array, optional
            voltage values.
        time_range : list of [float, float], optional
            Time range to restrict signal to.
            If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results
        they will be cleared by this method call.
        """

        # If any data is already present, then clear previous data
        # Also clear results, if present, unless indicated not to
        #   This is to ensure object consistency of all data & results
        self._reset_data_results(clear_time=self.has_data,
                                clear_signal=self.has_data,
                                clear_results=self.has_model and clear_results)
        self.time, self.signal, self.time_range, self.fs, self.time_res = \
            self._prepare_data(time, signal, time_range, signal_dim=1) 


    def add_settings(self, ERPparam_settings):
        """Add settings into object from a ERPparamSettings object.

        Parameters
        ----------
        ERPparam_settings : ERPparamSettings
            A data object containing the settings for a ERPparam model.
        """

        for setting in OBJ_DESC['settings']:
            setattr(self, setting, getattr(ERPparam_settings, setting))

        self._check_loaded_settings(ERPparam_settings._asdict())


    def add_meta_data(self, ERPparam_meta_data):
        """Add data information into object from a ERPparamMetaData object.

        Parameters
        ----------
        ERPparam_meta_data : ERPparamMetaData
            A meta data object containing meta data information.
        """

        for meta_dat in OBJ_DESC['meta_data']:
            setattr(self, meta_dat, getattr(ERPparam_meta_data, meta_dat))


    def add_results(self, ERPparam_result):
        """Add results data into object from a ERPparamResults object.

        Parameters
        ----------
        ERPparam_result : ERPparamResults
            A data object containing the results from fitting a ERPparam model.
        """

        self.gaussian_params_ = ERPparam_result.gaussian_params
        self.peak_params_ = ERPparam_result.peak_params
        self.r_squared_ = ERPparam_result.r_squared
        self.error_ = ERPparam_result.error

        self._check_loaded_results(ERPparam_result._asdict())


    def report(self, time=None, signal=None, time_range=None, **plot_kwargs):
        """Run model fit, and display a report, which includes a plot, 
        and printed results.

        Parameters
        ----------
        time : 1d array, optional
            Time values for the signal,.
        signal : 1d array, optional
            voltage values, which must be input.
        time_range : list of [float, float], optional
            Desired time range to fit the model to.
            If not provided, fits across the entire given range.
        **plot_kwargs
            Keyword arguments to pass into the plot method.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If time & signal provided together, add data to object.
        if time is not None and signal is not None:
            self.add_data(time, signal)

        self.fit(self.time, self.signal, time_range=time_range)
        self.plot(**plot_kwargs)
        self.print_results(concise=False)


    def fit(self, time=None, signal=None, time_range=None):
        """Fit the signal as a combination of periodic components (Gaussian peaks).

        Parameters
        ----------
        time : 1d array, optional
            Time values for the signal.
        signal : 1d array, optional
            voltage values, which must be input.
        time_range : list of [float, float], optional
            Time range to restrict signal to. If not provided, keeps the entire range.

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

        # If time & signal provided together, add data to object.
        if time is not None and signal is not None:
            self.add_data(time, signal, time_range)

        # If signal provided alone, add to object
        #   Note: be careful passing in power_spectrum data like this:
        elif isinstance(signal, np.ndarray):
            self.signal = signal

        # Check that data is available
        if not self.has_data:
            raise NoDataError("No data available to fit, can not proceed.")

        # Check and warn about width limits (if in verbose mode)
        if self.verbose:
            self._check_width_limits()

        # In rare cases, the model fails to fit, and so uses try / except
        try:

            # If not set to fail on NaN or Inf data at add time, check data here
            #   This serves as a catch all for curve_fits which will fail given NaN or Inf
            #   Because FitError's are by default caught, this allows fitting to continue
            if not self._check_data:
                if np.any(np.isinf(self.signal)) or np.any(np.isnan(self.signal)):
                    raise FitError("Model fitting was skipped because there are NaN or Inf "
                                   "values in the data, which preclude model fitting.")

            # Find peaks, and fit them with gaussians
            self.gaussian_params_ = self._fit_peaks(np.copy(self.signal))

            # Calculate the peak fit
            #   Note: if no peaks are found, this creates a flat (all zero) peak fit
            self._peak_fit = gen_periodic(self.time, np.ndarray.flatten(self.gaussian_params_))

            # Convert gaussian definitions to peak parameters
            self.peak_params_  = self._create_peak_params(self.gaussian_params_)

            # compute rise-decay symmetry
            self.shape_params_, self.peak_indices_ = self._compute_shape_params(self.peak_params_)

            # drop peaks based on edge proximity (if shape could not be fit)
            self._drop_peaks_near_edge()
            self.peak_indices_ = self.peak_indices_.astype(int)

            # Calculate R^2 and error of the model fit
            self._calc_r_squared()
            self._calc_error()

        except FitError:

            # If in debug mode, re-raise the error
            if self._debug:
                raise

            # Clear any interim model results that may have run
            #   Partial model results shouldn't be interpreted in light of overall failure
            self._reset_data_results(clear_results=True)

            # Print out status
            if self.verbose:
                print("Model fitting was unsuccessful.")


    def print_settings(self, description=False, concise=False):
        """Print out the current settings.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_settings_str(self, description, concise))


    def print_results(self, concise=False):
        """Print out model fitting results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_results_fm_str(self, concise))


    @staticmethod
    def print_report_issue(concise=False):
        """Prints instructions on how to report bugs and/or problematic fits.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_issue_str(concise))


    def get_settings(self):
        """Return user defined settings of the current object.

        Returns
        -------
        ERPparamSettings
            Object containing the settings from the current object.
        """

        sets = {key : getattr(self, key) for key in OBJ_DESC['settings']}
               # # ERPparamSettings(**{key : getattr(self, key) \
               #              for key in OBJ_DESC['settings']})
        return sets# {key:getattr(sets,key) for key in sets}


    def get_meta_data(self):
        """Return data information from the current object.

        Returns
        -------
        ERPparamMetaData
            Object containing meta data from the current object.
        """

        return ERPparamMetaData(**{key : getattr(self, key) \
                             for key in OBJ_DESC['meta_data']})


    def get_params(self, name, col=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'peak_params', 'gaussian_params', 'shape_params', 'error', 'r_squared'}
            Name of the data field to extract.
        col : {'CT', 'PW', 'BW'}, {'MN','HT','SD'}, {fwhm, rise_time, decay_time, symmetry,
            sharpness, sharpness_rise, sharpness_decay} or int, optional
            Column name / index to extract from selected data, if requested.
            Only used for name of {'peak_params', 'gaussian_params', 'shape_params}, 
            respectively.

        Returns
        -------
        out : float or 1d array
            Requested data.

        Raises
        ------
        NoModelError
            If there are no model fit parameters available to return.

        Notes
        -----
        If there are no fit peak (no peak parameters), this method will return NaN.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available to extract, can not proceed.")

        # Allow for shortcut alias, without adding `_params`
        if name in ['peak', 'gaussian', 'shape']:
            name = name + '_params'

        # If col specified as string, get mapping back to integer
        if isinstance(col, str):
            col = get_indices(name)[col]            

        # Extract the request data field from object
        out = getattr(self, name + '_')

        # Periodic values can be empty arrays and if so, replace with NaN array
        if isinstance(out, np.ndarray) and out.size == 0:
            out = np.array([np.nan, np.nan, np.nan])

        # Select out a specific column, if requested
        if col is not None:

            # Extract column, & if result is a single value in an array, unpack from array
            out = out[col] if out.ndim == 1 else out[:, col]
            out = out[0] if isinstance(out, np.ndarray) and out.size == 1 else out

        return out


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics.

        Returns
        -------
        ERPparamResults
            Object containing the model fit results from the current object.
        """

        return ERPparamResults(**{key.strip('_') : getattr(self, key) \
            for key in OBJ_DESC['results']})


    # @copy_doc_func_to_method(plot_fm)
    # def plot(self, plot_peaks=None, plot_aperiodic=True, plt_log=False,
    #          add_legend=True, save_fig=False, file_name=None, file_path=None,
    #          ax=None, data_kwargs=None, model_kwargs=None,
    #          aperiodic_kwargs=None, peak_kwargs=None, **plot_kwargs):

    #     plot_fm(self, plot_peaks=plot_peaks, plot_aperiodic=plot_aperiodic, plt_log=plt_log,
    #             add_legend=add_legend, save_fig=save_fig, file_name=file_name,
    #             file_path=file_path, ax=ax, data_kwargs=data_kwargs, model_kwargs=model_kwargs,
    #             aperiodic_kwargs=aperiodic_kwargs, peak_kwargs=peak_kwargs, **plot_kwargs)
    @copy_doc_func_to_method(plot_ERPparam)
    def plot(self, ax=None, y_label=None):

        plot_ERPparam(self, ax=ax, y_label=y_label)


    @copy_doc_func_to_method(save_report_fm)
    def save_report(self, file_name, file_path=None,
                    add_settings=True, **plot_kwargs):

        save_report_fm(self, file_name, file_path, add_settings, **plot_kwargs)


    @copy_doc_func_to_method(save_fm)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fm(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None, regenerate=True):
        """Load in a ERPparam formatted JSON file to the current object.

        Parameters
        ----------
        file_name : str or FileObject
            File to load data from.
        file_path : str or None, optional
            Path to directory to load from. If None, loads from current directory.
        regenerate : bool, optional, default: True
            Whether to regenerate the model fit from the loaded data, if data is available.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data_results(True, True, True)

        # Load JSON file, add to self and check loaded data
        data = load_json(file_name, file_path)
        self._add_from_dict(data)
        self._check_loaded_settings(data)
        self._check_loaded_results(data)

        # Regenerate model components, based on what is available
        if regenerate:
            if self.time_range and self.fs:
                self._regenerate_time_vector()
            if np.all(self.time) and np.all(self.gaussian_params_):
                self._regenerate_model()


    def copy(self):
        """Return a copy of the current object."""

        return deepcopy(self)


    def set_debug_mode(self, debug):
        """Set debug mode, which controls if an error is raised if model fitting is unsuccessful.

        Parameters
        ----------
        debug : bool
            Whether to run in debug mode.
        """

        self._debug = debug


    def set_check_data_mode(self, check_data):
        """Set check data mode, which controls if an error is raised if NaN or Inf data are added.

        Parameters
        ----------
        check_data : bool
            Whether to run in check data mode.
        """

        self._check_data = check_data


    def to_df(self, peak_org):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.

        Returns
        -------
        pd.Series
            Model results organized into a pandas object.
        """

        return model_to_dataframe(self.get_results(), peak_org)


    def _check_width_limits(self):
        """Check and warn about peak width limits / sampling frequency interaction."""

        # Check peak width limits against time resolution and warn if too close
        if 1.5 * (1/self.fs) >= self.peak_width_limits[0]:
            print(gen_width_warning_str((1/self.fs), self.peak_width_limits[0]))


    def _fit_peaks(self, iter_signal):
        """Iteratively fit peaks to the signal.

        Parameters
        ----------
        iter_signal : 1d array
            Evoked response to be fit.

        Returns
        -------
        gaussian_params : 2d array
            Parameters that define the gaussian fit(s).
            Each row is a gaussian, as [mean, height, standard deviation].
        """

        # Initialize matrix of guess parameters for gaussian fitting
        guess = np.empty([0, 3])

        # Find peak: Loop through, finding a candidate peak, and fitting with a guess gaussian
        #   Stopping procedures: limit on # of peaks, or relative or absolute height thresholds
        while len(guess) < self.max_n_peaks:

            # Find candidate peak - the maximum point of the signal
            max_ind = np.argmax(iter_signal)
            min_ind = np.argmin(iter_signal)
            if np.abs(iter_signal[min_ind]) > np.abs(iter_signal[max_ind]):
                max_ind = min_ind
            max_height = iter_signal[max_ind]

            # Stop searching for peaks once height drops below height threshold
            if np.abs(max_height) <= self.peak_threshold * np.std(iter_signal):
                break

            # Set the guess parameters for gaussian fitting, specifying the mean and height
            guess_time = self.time[max_ind]
            guess_height = max_height

            # Halt fitting process if candidate peak drops below minimum height
            if not np.abs(guess_height) > self.min_peak_height:
                break

            # Data-driven first guess at standard deviation
            #   Find half height index on each side of the center frequency
            half_height = 0.5 * max_height
            le_ind = next((val for val in range(max_ind - 1, 0, -1)
                           if iter_signal[val] <= half_height), None)
            ri_ind = next((val for val in range(max_ind + 1, len(iter_signal), 1)
                           if iter_signal[val] <= half_height), None)

            # Guess bandwidth procedure: estimate the width of the peak
            try:
                # Get an estimated width from the shortest side of the peak
                #   We grab shortest to avoid estimating very large values from overlapping peaks
                # Grab the shortest side, ignoring a side if the half max was not found
                short_side = min([abs(ind - max_ind) \
                    for ind in [le_ind, ri_ind] if ind is not None])

                # Use the shortest side to estimate full-width, half max (converted to Hz)
                #   and use this to estimate that guess for gaussian standard deviation
                fwhm = short_side * 2 * (1/self.fs)
                guess_std = compute_gauss_std(fwhm)

            except ValueError:
                # This procedure can fail (very rarely), if both left & right inds end up as None
                #   In this case, default the guess to the average of the peak width limits
                guess_std = np.mean(self.peak_width_limits)

            # Check that guess value isn't outside preset limits - restrict if so
            #   Note: without this, curve_fitting fails if given guess > or < bounds
            if guess_std < self._gauss_std_limits[0]:
                guess_std = self._gauss_std_limits[0]
            if guess_std > self._gauss_std_limits[1]:
                guess_std = self._gauss_std_limits[1]

            # Collect guess parameters and subtract this guess gaussian from the data
            guess = np.vstack((guess, (guess_time, guess_height, guess_std)))
            peak_gauss = gaussian_function(self.time, guess_time, guess_height, guess_std)
            iter_signal = iter_signal - peak_gauss

        # Check peaks based on edges, and on overlap, dropping any that violate requirements
        guess = self._drop_peak_cf(guess)
        guess = self._drop_peak_overlap(guess)

        # If there are peak guesses, fit the peaks, and sort results
        if len(guess) > 0:
            gaussian_params = self._fit_peak_guess(guess)
            gaussian_params = gaussian_params[gaussian_params[:, 0].argsort()]
        else:
            gaussian_params = np.empty([0, 3])

        return gaussian_params


    def _fit_peak_guess(self, guess):
        """Fits a group of peak guesses with a fit function.

        Parameters
        ----------
        guess : 2d array, shape=[n_peaks, 3]
            Guess parameters for gaussian fits to peaks, as gaussian parameters.

        Returns
        -------
        gaussian_params : 2d array, shape=[n_peaks, 3]
            Parameters for gaussian fits to peaks, as gaussian parameters.
        """

        # Set the bounds for CT, enforce positive height value, and set bandwidth limits
        #   Note that 'guess' is in terms of gaussian std, so +/- BW is 2 * the guess_gauss_std
        #   This set of list comprehensions is a way to end up with bounds in the form:
        #     ((cf_low_peak1, height_low_peak1, bw_low_peak1, *repeated for n_peaks*),
        #      (cf_high_peak1, height_high_peak1, bw_high_peak, *repeated for n_peaks*))
        #     ^where each value sets the bound on the specified parameter
        lo_bound = [[peak[0] - 2 * self._cf_bound * peak[2], -np.inf, self._gauss_std_limits[0]]
                    for peak in guess]
        hi_bound = [[peak[0] + 2 * self._cf_bound * peak[2], np.inf, self._gauss_std_limits[1]]
                    for peak in guess]

        # Check that CT bounds are within time range
        #   If they are  not, update them to be restricted to time range
        lo_bound = [bound if bound[0] > self.time_range[0] else \
            [self.time_range[0], *bound[1:]] for bound in lo_bound]
        hi_bound = [bound if bound[0] < self.time_range[1] else \
            [self.time_range[1], *bound[1:]] for bound in hi_bound]

        # Unpacks the embedded lists into flat tuples
        #   This is what the fit function requires as input
        gaus_param_bounds = (tuple(item for sublist in lo_bound for item in sublist),
                             tuple(item for sublist in hi_bound for item in sublist))

        # Flatten guess, for use with curve fit
        guess = np.ndarray.flatten(guess)

        # Fit the peaks
        try:
            gaussian_params, _ = curve_fit(gaussian_function, self.time, self.signal,
                                        p0=guess, maxfev=self._maxfev, bounds=gaus_param_bounds)
        except RuntimeError as excp:
            error_msg = ("Model fitting failed due to not finding "
                         "parameters in the peak component fit.")
            raise FitError(error_msg) from excp
        except LinAlgError as excp:
            error_msg = ("Model fitting failed due to a LinAlgError during peak fitting. "
                         "This can happen with settings that are too liberal, leading, "
                         "to a large number of guess peaks that cannot be fit together.")
            raise FitError(error_msg) from excp

        # Re-organize params into 2d matrix
        gaussian_params = np.array(group_three(gaussian_params))

        return gaussian_params


    def _create_peak_params(self, gaus_params):
        """Copies over the gaussian params to peak outputs, updating as appropriate.

        Parameters
        ----------
        gaus_params : 2d array
            Parameters that define the gaussian fit(s), as gaussian parameters.

        Returns
        -------
        peak_params : 2d array
            Fitted parameter values for the peaks, with each row as [CT, PW, BW].

        Notes
        -----
        The gaussian center is unchanged as the peak center.

        The gaussian height is updated to reflect the height of the signal. This is 
        returned instead of the gaussian height, as the gaussian height is harder to interpret, 
        due to peak overlaps.

        The gaussian standard deviation is updated to be 'both-sided', to reflect the
        'bandwidth' of the peak, as opposed to the gaussian parameter, which is 1-sided.

        Performing this conversion requires that the model has been run.
        """

        peak_params = np.empty((len(gaus_params), 3))

        for ii, peak in enumerate(gaus_params):

            # find the maximum height of the signal within _gauss_overlap_thresh of the peak
            peak_range = np.where(np.logical_and(self.time >= peak[0] - peak[2] * self._gauss_overlap_thresh,
                                                    self.time <= peak[0] + peak[2] * self._gauss_overlap_thresh))
            peak_index = np.argmax(np.abs(self.signal[peak_range])) + peak_range[0][0]

            # Collect peak parameter data
            peak_params[ii] = [self.time[peak_index], self.signal[peak_index], peak[2] * 2]

        return peak_params


    def _get_peak_indices(self, peak_params):
        """
        Find the indices of the peak and the half magnitude points.
        """

        # compute half magnitude
        half_mag = peak_params[1] / 2

        # get index of peak
        peak_index = np.argmin(np.abs(self.time - peak_params[0]))

        # find the index closest to the peak that crosses the half magnitude
        try:
            if self.signal[peak_index]>0:
                start_index = np.argwhere((self.signal[:peak_index] - half_mag)<0)[-1][0]
                end_index = peak_index + np.argwhere(-(self.signal[peak_index:] - half_mag)>0)[0][0]
            else: # flip the logic if the peak is negative
                start_index = np.argwhere((self.signal[:peak_index] - half_mag)>0)[-1][0]
                end_index = peak_index + np.argwhere(-(self.signal[peak_index:] - half_mag)<0)[0][0]
        except IndexError:
            # if the half magnitude is not crossed, set the start and end indices to NaN
            start_index = np.nan
            end_index = np.nan

        return start_index, peak_index, end_index


    def _compute_shape_params(self, peak_params):
        """
        Compute the ERP shape parameters.
        
        Returns
        -------
        shape_params : list
            List of shape parameters. In order:
            * FWHM: full width at half magnitude
            * rise_time: rise time i.e. time between peak and rising half-magnitude point
            * decay_time: decay time i.e. time between peak and decaying half-magnitude point
            * symmetry: rise time / FWHM
            * sharpness: peak sharpness (normalized to be dimensionless 0-1)
            * sharpness_rise: sharpness of the rise (normalized to be dimensionless 0-1)
            * sharpness_decay: sharpness of the decay (normalized to be dimensionless 0-1)
        """

        # initialize list of shape parameters
        shape_params = np.empty((len(peak_params), 7))
        peak_indices = np.empty((len(peak_params), 3))

        for ii, peak in enumerate(peak_params):

            # get peak indices
            start_index, peak_index, end_index = self._get_peak_indices(peak)

            # if the peak indices could not be determined, set all shape params to NaN
            if np.isnan(start_index) or np.isnan(end_index):
                shape_params[ii] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
                peak_indices[ii] = [np.nan, np.nan, np.nan]
                continue

            # compute fwhm, rise-, and decay-time
            fwhm = self.time[end_index] - self.time[start_index]
            rise_time = self.time[peak_index] - self.time[start_index]
            decay_time = self.time[end_index] - self.time[peak_index]

            # compute rise-decay symmetry
            rise_decay_symmetry = rise_time / fwhm

            # compute sharpness
            half_mag = np.abs(peak[1] / 2)
            sharpness_rise = np.arctan(half_mag / rise_time) * (180 / np.pi) / 90
            sharpness_decay = np.arctan(half_mag / decay_time) * (180 / np.pi) / 90
            sharpness = 1 - ((180 - ((np.arctan(half_mag / rise_time) * (180 / np.pi)) + (np.arctan(half_mag / decay_time)) * (180 / np.pi))) / 180)

            # collect results
            shape_params[ii] = [fwhm, rise_time, decay_time, rise_decay_symmetry,
                             sharpness, sharpness_rise, sharpness_decay]
            peak_indices[ii] = [start_index, peak_index, end_index]

        return shape_params, peak_indices


    def _drop_peak_cf(self, guess):
        """Check whether to drop peaks based on center's proximity to the edge of the signal.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian peak fits. Shape: [n_peaks, 3].

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian peak fits. Shape: [n_peaks, 3].
        """

        cf_params = guess[:, 0]
        bw_params = guess[:, 2] * self._bw_std_edge

        # Check if peaks within drop threshold from the edge of the time range
        keep_peak = \
            (np.abs(np.subtract(cf_params, self.time_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.time_range[1])) > bw_params)

        # Drop peaks that fail the center edge criterion
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _drop_peak_overlap(self, guess):
        """Checks whether to drop gaussians based on amount of overlap.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian peak fits. Shape: [n_peaks, 3].

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian peak fits. Shape: [n_peaks, 3].

        Notes
        -----
        For any gaussians with an overlap that crosses the threshold,
        the lowest height guess Gaussian is dropped.
        """

        # Sort the peak guesses sequentially
        #   This is so adjacent peaks can be compared from right to left
        guess = sorted(guess, key=lambda x: float(x[0]))

        # Calculate standard deviation bounds for checking amount of overlap
        #   The bounds are the gaussian peak time +/- gaussian standard deviation
        bounds = [[peak[0] - peak[2] * self._gauss_overlap_thresh,
                   peak[0] + peak[2] * self._gauss_overlap_thresh] for peak in guess]

        # Loop through peak bounds, comparing current bound to that of next peak
        #   If the left peak's upper bound extends pass the right peaks lower bound,
        #   then drop the Gaussian with the lower height
        drop_inds = []
        for ind, b_0 in enumerate(bounds[:-1]):
            b_1 = bounds[ind + 1]

            # Check if bound of current peak extends into next peak
            if b_0[1] > b_1[0]:

                # If so, get the index of the gaussian with the lowest height (to drop)
                drop_inds.append([ind, ind + 1][np.argmin([guess[ind][1], guess[ind + 1][1]])])

        # Drop any peaks guesses that overlap too much, based on threshold
        keep_peak = [not ind in drop_inds for ind in range(len(guess))]
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _drop_peaks_near_edge(self):
        """Check whether to drop peaks based on shape parameter fitting. If a peak is too close to 
        the edge of the signal, the half-magnitude points cannott be determined, and the shape
        parameters will be set to NaN.
        """

        to_drop = np.isnan(self.peak_indices_).any(axis=1)
        self.gaussian_params_ = self.gaussian_params_[~to_drop]
        self.peak_params_ = self.peak_params_[~to_drop]
        self.shape_params_ = self.shape_params_[~to_drop]
        self.peak_indices_ = self.peak_indices_[~to_drop]


    def _calc_r_squared(self):
        """Calculate the r-squared goodness of fit of the model, compared to the original data."""

        r_val = np.corrcoef(self.signal, self._peak_fit)
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
            self.error_ = np.abs(self.signal - self._peak_fit).mean()

        elif metric == 'MSE':
            self.error_ = ((self.signal - self._peak_fit) ** 2).mean()

        elif metric == 'RMSE':
            self.error_ = np.sqrt(((self.signal - self._peak_fit) ** 2).mean())

        else:
            msg = "Error metric '{}' not understood or not implemented.".format(metric)
            raise ValueError(msg)


    def _prepare_data(self, time, signal, time_range=None, signal_dim=1):
        """Prepare input data for adding to current object.

        Parameters
        ----------
        time : 1d array, optional
            Time values for the signal.
        signal : 1d array
            ERP timeseries
            1d vector, or 2d as [n_ERPs, n_times].
        time_range : list of [float, float]
            Time range to restrict signal to. If None, keeps the entire range.
        signal_dim : int, optional, default: 1
            Dimensionality that the signal should have.

        Returns
        -------
        signal : 1d or 2d array
            signal (trimmed in time range, if desired)
        time_range : list of [float, float]
            Minimum and maximum values of the time vector.

        Raises
        ------
        DataError
            If there is an issue with the data.
        InconsistentDataError
            If the input data are inconsistent size.
        """

        # print(signal_dim)
        # print(signal.ndim)
        # Check that data are the right types
        if not isinstance(time, np.ndarray) or not isinstance(signal, np.ndarray):
            raise DataError("Input data must be numpy arrays.")

        # Check that data have the right dimensionality
        if time.ndim != 1 or (signal.ndim != signal_dim):
            raise DataError("Inputs are not the right dimensions.")

        # Check that data sizes are compatible
        if time.shape[-1] != signal.shape[-1]:
            raise InconsistentDataError("The input times and ERP signal "
                                        "are not a consistent size.")

        # Force data to be dtype of float64
        #   If they end up as float32, or less, scipy curve_fit fails (sometimes implicitly)
        if time.dtype != 'float64':
            time = time.astype('float64')
        if signal.dtype != 'float64':
            signal = signal.astype('float64')

        # Check time range, trim the signal range if requested
        if time_range:
            time, signal = trim_spectrum(time, signal, time_range)

        # Calculate temporal resolution, and actual time range of the data
        time_range = [time.min(), time.max()]
        time_res = np.abs(time[1] - time[0])
        fs = 1 / time_res

        ## Data checks - run checks on inputs based on check modes

        if self._check_times:
            # Check if the time data is unevenly spaced, and raise an error if so
            time_diffs = np.diff(time)
            if not np.all(np.isclose(time_diffs, time_res)):
                raise DataError("The input time values are not evenly spaced. "
                                "The model expects equidistant time values.")
        if self._check_data:
            # Check if there are any infs / nans, and raise an error if so
            if np.any(np.isinf(signal)) or np.any(np.isnan(signal)):
                error_msg = ("The input data contains NaNs or Infs. "
                             "This will cause the fitting to yield NaNs. ")
                raise DataError(error_msg)
            
        return time, signal, time_range, fs, time_res


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        # Reconstruct object from loaded data
        for key in data.keys():
            setattr(self, key, data[key])


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

        # Reset internal settings so that they are consistent with what was loaded
        #   Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _regenerate_time_vector(self):
        """Regenerate the time vector, given the object metadata."""

        self.time = gen_time_vector(self.time_range, self.fs)


    def _regenerate_model(self):
        """Regenerate model fit from parameters."""

        self._peak_fit = gen_periodic(
            self.time,  np.ndarray.flatten(self.gaussian_params_))
