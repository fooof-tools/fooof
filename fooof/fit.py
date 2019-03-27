"""FOOOF - Fitting Oscillations & One-Over F.

Notes
-----
Methods without defined docstrings import docs at runtime, from aliased external functions.
Private attributes of the FOOOF method, not publicly exposed, are documented below.

Private Attributes
------------------
_spectrum_flat : 1d array
    Flattened power spectrum (aperiodic component removed).
_spectrum_peak_rm : 1d array
    Power spectrum with peaks removed (not flattened).
_gaussian_params : 2d array
    Parameters that define the gaussian fit(s).
    Each row is a gaussian, as [mean, height, standard deviation].
_ap_fit : 1d array
    Values of the aperiodic fit.
_peak_fit : 1d array
    Values of the peak fit (flattened).
_ap_percentile_thresh : float
    Percentile threshold for finding peaks above the aperiodic component.
_ap_guess : list of [float, float, float]
    Guess parameters for fitting the aperiodic component.
_ap_bounds : tuple of tuple of float
    Upper and lower bounds on fitting aperiodic component.
_bw_std_edge : float
    Bandwidth threshold for edge rejection of peaks, in units of gaussian standard deviation.
_gauss_overlap_thresh : float
    Degree of overlap (in units of guassian std. deviation) between gaussian guesses to drop one.
_gauss_std_limits : list of [float, float]
    Peak width limits, converted to use for gaussian standard deviation parameter.
"""

import warnings
from copy import deepcopy

import numpy as np
from scipy.optimize import curve_fit

from fooof.core.io import save_fm, load_json
from fooof.core.reports import save_report_fm
from fooof.core.funcs import gaussian_function, get_ap_func, infer_ap_func
from fooof.core.utils import group_three, check_array_dim
from fooof.core.info import get_obj_desc
from fooof.core.modutils import copy_doc_func_to_method
from fooof.core.strings import gen_settings_str, gen_results_str_fm, gen_issue_str, gen_wid_warn_str

from fooof.plts.fm import plot_fm
from fooof.utils import trim_spectrum
from fooof.data import FOOOFResults, FOOOFSettings, FOOOFDataInfo
from fooof.sim.gen import gen_freqs, gen_aperiodic, gen_peaks

###################################################################################################
###################################################################################################

class FOOOF():
    """Model the physiological power spectrum as a combination of aperiodic and periodic components.

    WARNING: FOOOF expects frequency and power values in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    peak_width_limits : tuple of (float, float), optional, default: (0.5, 12.0)
        Limits on possible peak width, as (lower_bound, upper_bound).
    max_n_peaks : int, optional, default: inf
        Maximum number of gaussians to be fit in a single spectrum.
    min_peak_height : float, optional, default: 0
        Absolute threshold for detecting peaks, in units of the input data.
    peak_threshold : float, optional, default: 2.0
        Relative threshold for detecting peaks, in units of standard deviation of the input data.
    aperiodic_mode : {'fixed', 'knee'}
        Which approach to take for fitting the aperiodic component.
    verbose : boolean, optional, default: True
        Whether to be verbose in printing out warnings.

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the power spectrum.
    power_spectrum : 1d array
        Power values, stored internally in log10 scale.
    freq_range : list of [float, float]
        Frequency range of the power spectrum, as [lowest_freq, highest_freq].
    freq_res : float
        Frequency resolution of the power spectrum.
    fooofed_spectrum_ : 1d array
        The full model fit of the power spectrum, in log10 scale
    aperiodic_params_ : 1d array
        Parameters that define the aperiodic fit. As [Offset, (Knee), Exponent].
        The knee parameter is only included if aperiodic component is fit with a knee.
    peak_params_ : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CF, PW, BW].
    r_squared_ : float
        R-squared of the fit between the input power spectrum and the full model fit.
    error_ : float
        Root mean squared error of the full model fit.

    Notes
    -----
    - Commonly used abbreviations used in FOOOF include
      CF: center frequency, PW: power, BW: Bandwidth, ap: aperiodic
    - Input power spectra must be provided in linear scale.
      Internally they are stored in log10 scale, as this is what the model operates upon.
    - Input power spectra should be smooth, as overly noisy power spectra may lead to bad fits.
      In particular, raw FFT inputs are not appropriate, we recommend using either Welch's
      procedure, or a median filter smoothing on the FFT output before running FOOOF.
    - Where possible and appropriate, use longer time segments for power spectrum calculation to
      get smoother power spectra, as this will give better FOOOF fits.
    """

    def __init__(self, peak_width_limits=(0.5, 12.0), max_n_peaks=np.inf, min_peak_height=0.0,
                 peak_threshold=2.0, aperiodic_mode='fixed', verbose=True):
        """Initialize FOOOF object with run parameters."""

        # Double check correct scipy version is being used
        from scipy import __version__
        major, minor, _ = __version__.split('.')
        if int(major) < 1 and int(minor) < 19:
            raise ImportError('Scipy version of >= 0.19.0 required.')

        # Set input parameters
        self.peak_width_limits = peak_width_limits
        self.max_n_peaks = max_n_peaks
        self.min_peak_height = min_peak_height
        self.peak_threshold = peak_threshold
        self.aperiodic_mode = aperiodic_mode
        self.verbose = verbose

        ## SETTINGS - these are updateable by the user if required.
        # Noise threshold, as a percentage of the lowest magnitude values in the total data to fit.
        #  Defines the minimum height, above residuals, to be considered a peak.
        self._ap_percentile_thresh = 0.025
        # Guess parameters for aperiodic fitting, [offset, knee, exponent]
        #  If offset guess is None, the first value of the power spectrum is used as offset guess
        self._ap_guess = (None, 0, 2)
        # Bounds for aperiodic fitting, as: ((offset_low_bound, knee_low_bound, sl_low_bound),
        #                                    (offset_high_bound, knee_high_bound, sl_high_bound))
        # By default, aperiodic fitting is unbound, but can be restricted here, if desired
        #   Even if fitting without knee, leave bounds for knee (they are dropped later)
        self._ap_bounds = ((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf))
        # Threshold for how far (units of gaus std dev) a peak has to be from edge to keep.
        self._bw_std_edge = 1.0
        # Degree of overlap  (units of gauss std dev) between gaussians for one to be dropped
        self._gauss_overlap_thresh = 1.5
        # Parameter bounds for center frequency when fitting gaussians - in terms of +/- std dev
        self._cf_bound = 1.5

        # Set internal settings (based on inputs). Initialize data & results attributes.
        self._reset_internal_settings()
        self._reset_data_results()


    def _reset_internal_settings(self):
        """Set (or reset) internal settings, based on what is provided in init.

        Notes
        -----
        These settings are for internal use, based on what is provided to, or set in `__init__`.
        They should not be altered by the user.
        """

        # Only update these settings if other relevant settings are available
        if self.peak_width_limits:

            # Bandwidth limits are given in 2-sided peak bandwidth.
            #  Convert to gaussian std parameter limits.
            self._gauss_std_limits = tuple([bwl / 2 for bwl in self.peak_width_limits])
            # Bounds for aperiodic fitting. Drops bounds on knee parameter if not set to fit knee
            self._ap_bounds = self._ap_bounds if self.aperiodic_mode == 'knee' \
                else tuple(bound[0::2] for bound in self._ap_bounds)

        # Otherwise, assume settings are unknown (have been cleared) and set to None
        else:
            self._gauss_std_limits = None
            self._ap_bounds = None


    def _reset_data_results(self, clear_freqs=True, clear_spectrum=True, clear_results=True):
        """Set (or reset) data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: True
            Whether to clear frequency attributes.
        clear_power_spectrum : bool, optional, default: True
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: True
            Whether to clear model results attributes.
        """

        if clear_freqs:
            self.freqs = None
            self.freq_range = None
            self.freq_res = None

        if clear_spectrum:
            self.power_spectrum = None

        if clear_results:
            self.aperiodic_params_ = None
            self.peak_params_ = None
            self.r_squared_ = None
            self.error_ = None
            self._gaussian_params = None

            self.fooofed_spectrum_ = None

            self._spectrum_flat = None
            self._spectrum_peak_rm = None
            self._ap_fit = None
            self._peak_fit = None


    def add_data(self, freqs, power_spectrum, freq_range=None):
        """Add data (frequencies and power spectrum values) to FOOOF object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array
            Power spectrum values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        they will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if np.any(self.freqs):
            self._reset_data_results()

        self.freqs, self.power_spectrum, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, power_spectrum, freq_range, 1, self.verbose)


    def add_settings(self, fooof_settings):
        """Add settings into object from a FOOOFSettings object.

        Parameters
        ----------
        fooof_settings : FOOOFSettings
            A FOOOF data object containing the settings for a FOOOF model.
        """

        for setting in get_obj_desc()['settings']:
            setattr(self, setting, getattr(fooof_settings, setting))

        self._check_loaded_settings(fooof_settings._asdict())


    def add_data_info(self, fooof_data_info):
        """Add data information into object from a FOOOFDataInfo object.

        Parameters
        ----------
        fooof_data_info : FOOOFDataInfo
            A FOOOF data object containing information about the data.
        """

        for data_info in get_obj_desc()['data_info']:
            setattr(self, data_info, getattr(fooof_data_info, data_info))

        self._regenerate_freqs()


    def add_results(self, fooof_result):
        """Add results data into object from a FOOOFResults object.

        Parameters
        ----------
        fooof_result : FOOOFResults
            A FOOOF data object containing the results from fitting a FOOOF model.
        """

        self.aperiodic_params_ = fooof_result.aperiodic_params
        self.peak_params_ = fooof_result.peak_params
        self.r_squared_ = fooof_result.r_squared
        self.error_ = fooof_result.error
        self._gaussian_params = fooof_result.gaussian_params

        self._check_loaded_results(fooof_result._asdict())


    def report(self, freqs=None, power_spectrum=None, freq_range=None, plt_log=False):
        """Run model fit, and display a report, which includes a plot, and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum.
        power_spectrum : 1d array, optional
            Power values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        plt_log : boolean, optional, default: False
            Whether or not to plot the frequency axis in log space.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        self.fit(freqs, power_spectrum, freq_range)
        self.plot(plt_log)
        self.print_results(False)


    def fit(self, freqs=None, power_spectrum=None, freq_range=None):
        """Fit the full power spectrum as a combination of periodic and aperiodic components.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array, optional
            Power values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to. If not provided, keeps the entire range.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        # If freqs & power_spectrum provided together, add data to object.
        if freqs is not None and power_spectrum is not None:
            self.add_data(freqs, power_spectrum, freq_range)
        # If power spectrum provided alone, add to object, and use existing frequency data
        #  Note: be careful passing in power_spectrum data like this:
        #    It assumes the power_spectrum is already logged, with correct freq_range.
        elif isinstance(power_spectrum, np.ndarray):
            self.power_spectrum = power_spectrum

        # Check that data is available
        if self.freqs is None or self.power_spectrum is None:
            raise ValueError('No data available to fit - can not proceed.')

        # Check and warn about width limits (if in verbose mode)
        if self.verbose:
            self._check_width_limits()

        # In rare cases, the model fails to fit. Therefore it's in a try/except
        #  Cause of failure: RuntimeError, failure to find parameters in curve_fit
        try:

            # Fit the aperiodic component
            self.aperiodic_params_ = self._robust_ap_fit(self.freqs, self.power_spectrum)
            self._ap_fit = gen_aperiodic(self.freqs, self.aperiodic_params_)

            # Flatten the power_spectrum using fit aperiodic fit
            self._spectrum_flat = self.power_spectrum - self._ap_fit

            # Find peaks, and fit them with gaussians
            self._gaussian_params = self._fit_peaks(np.copy(self._spectrum_flat))

            # Calculate the peak fit
            #  Note: if no peaks are found, this creates a flat (all zero) peak fit.
            self._peak_fit = gen_peaks(self.freqs, np.ndarray.flatten(self._gaussian_params))

            # Create peak-removed (but not flattened) power spectrum.
            self._spectrum_peak_rm = self.power_spectrum - self._peak_fit

            # Run final aperiodic fit on peak-removed power spectrum
            #   Note: This overwrites previous aperiodic fit
            self.aperiodic_params_ = self._simple_ap_fit(self.freqs, self._spectrum_peak_rm)
            self._ap_fit = gen_aperiodic(self.freqs, self.aperiodic_params_)

            # Create full power_spectrum model fit
            self.fooofed_spectrum_ = self._peak_fit + self._ap_fit

            # Convert gaussian definitions to peak parameters
            self.peak_params_ = self._create_peak_params(self._gaussian_params)

            # Calculate R^2 and error of the model fit.
            self._calc_r_squared()
            self._calc_rmse_error()

        # Catch failure, stemming from curve_fit process
        except RuntimeError:

            # Clear any interim model results that may have run
            #  Partial model results shouldn't be interpreted in light of overall failure
            self._reset_data_results(clear_freqs=False, clear_spectrum=False, clear_results=True)

            # Print out status
            if self.verbose:
                print('Model fitting was unsuccessful.')


    def print_settings(self, description=False, concise=False):
        """Print out the current FOOOF settings.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_settings_str(self, description, concise))


    def print_results(self, concise=False):
        """Print out FOOOF results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_results_str_fm(self, concise))


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
        """Return user defined settings of the FOOOF object.

        Returns
        -------
        FOOOFSettings
            Object containing the settings from the current FOOOF object.
        """

        return FOOOFSettings(**{key : getattr(self, key) for key in get_obj_desc()['settings']})


    def get_data_info(self):
        """Return data information from the FOOOF object.

        Returns
        -------
        FOOOFDataInfo
            Object containing information about the data from the current FOOOF object.
        """

        return FOOOFDataInfo(**{key : getattr(self, key) for key in get_obj_desc()['data_info']})


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics.

        Returns
        -------
        FOOOFResults
            Object containing the FOOOF model fit results from the current FOOOF object.
        """

        return FOOOFResults(**{key.strip('_') : getattr(self, key) for key in get_obj_desc()['results']})


    @copy_doc_func_to_method(plot_fm)
    def plot(self, plt_log=False, save_fig=False, file_name='FOOOF_plot', file_path=None, ax=None):

        plot_fm(self, plt_log, save_fig, file_name, file_path, ax)


    @copy_doc_func_to_method(save_report_fm)
    def save_report(self, file_name='FOOOF_report', file_path=None, plt_log=False):

        save_report_fm(self, file_name, file_path, plt_log)


    @copy_doc_func_to_method(save_fm)
    def save(self, file_name='FOOOF_results', file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fm(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name='FOOOF_results', file_path=None, regenerate=True):
        """Load in FOOOF file. Reads in a FOOOF formatted JSON file.

        Parameters
        ----------
        file_name : str or FileObject, optional
            File from which to load data.
        file_path : str, optional
            Path to directory from which to load. If not provided, loads from current directory.
        regenerate : bool, optional, default: True
            Whether to regenerate the model fit from the loaded data, if data is available.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data_results()

        # Load JSON file, add to self and check loaded data
        data = load_json(file_name, file_path)
        self._add_from_dict(data)
        self._check_loaded_settings(data)
        self._check_loaded_results(data)

        # Regenerate model components, based on what's available
        if regenerate:
            if self.freq_res:
                self._regenerate_freqs()
            if np.all(self.freqs) and np.all(self.aperiodic_params_):
                self._regenerate_model()


    def copy(self):
        """Return a copy of the FOOOF object."""

        return deepcopy(self)


    def _check_width_limits(self):
        """Check and warn about peak width limits / frequency resolution interaction."""

        # Check peak width limits against frequency resolution; warn if too close.
        if 1.5 * self.freq_res >= self.peak_width_limits[0]:
            print(gen_wid_warn_str(self.freq_res, self.peak_width_limits[0]))


    def _simple_ap_fit(self, freqs, power_spectrum):
        """Fit the aperiodic component of the power spectrum.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear scale.
        power_spectrum : 1d array
            Power values, in log10 scale.

        Returns
        -------
        aperiodic_params : 1d array
            Parameter estimates for aperiodic fit.
        """

        # Set guess params for lorentzian aperiodic fit, guess params set at init
        guess = np.array(([power_spectrum[0]] if not self._ap_guess[0] else [self._ap_guess[0]]) +
                         ([self._ap_guess[1]] if self.aperiodic_mode == 'knee' else []) +
                         [self._ap_guess[2]])

        # Ignore warnings that are raised in curve_fit
        #  A runtime warning can occur while exploring parameters in curve fitting
        #    This doesn't effect outcome - it won't settle on an answer that does this
        #  It happens if / when b < 0 & |b| > x**2, as it leads to log of a negative number
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            aperiodic_params, _ = curve_fit(get_ap_func(self.aperiodic_mode),
                                            freqs, power_spectrum, p0=guess,
                                            maxfev=5000, bounds=self._ap_bounds)

        return aperiodic_params


    def _robust_ap_fit(self, freqs, power_spectrum):
        """Fit the aperiodic component of the power spectrum robustly, ignoring outliers.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectrum, in linear scale.
        power_spectrum : 1d array
            Power values, in log10 scale.

        Returns
        -------
        aperiodic_params : 1d array
            Parameter estimates for aperiodic fit.
        """

        # Do a quick, initial aperiodic fit
        popt = self._simple_ap_fit(freqs, power_spectrum)
        initial_fit = gen_aperiodic(freqs, popt)

        # Flatten power_spectrum based on initial aperiodic fit
        flatspec = power_spectrum - initial_fit

        # Flatten outliers - any points that drop below 0
        flatspec[flatspec < 0] = 0

        # Use percential threshold, in terms of # of points, to extract and re-fit
        perc_thresh = np.percentile(flatspec, self._ap_percentile_thresh)
        perc_mask = flatspec <= perc_thresh
        freqs_ignore = freqs[perc_mask]
        spectrum_ignore = power_spectrum[perc_mask]

        # Second aperiodic fit - using results of first fit as guess parameters
        #  See note in _simple_ap_fit about warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            aperiodic_params, _ = curve_fit(get_ap_func(self.aperiodic_mode),
                                            freqs_ignore, spectrum_ignore, p0=popt,
                                            maxfev=5000, bounds=self._ap_bounds)

        return aperiodic_params


    def _fit_peaks(self, flat_iter):
        """Iteratively fit peaks to flattened spectrum.

        Parameters
        ----------
        flat_iter : 1d array
            Flattened power spectrum values.

        Returns
        -------
        gaussian_params : 2d array
            Parameters that define the gaussian fit(s).
            Each row is a gaussian, as [mean, height, standard deviation].
        """

        # Initialize matrix of guess parameters for gaussian fitting.
        guess = np.empty([0, 3])

        # Find peak: Loop through, finding a candidate peak, and fitting with a guass gaussian.
        #  Stopping procedure based on either # of peaks, or the relative or absolute height thresholds.
        while len(guess) < self.max_n_peaks:

            # Find candidate peak - the maximum point of the flattened spectrum.
            max_ind = np.argmax(flat_iter)
            max_height = flat_iter[max_ind]

            # Stop searching for peaks peaks once drops below height threshold.
            if max_height <= self.peak_threshold * np.std(flat_iter):
                break

            # Set the guess parameters for gaussian fitting - mean and height.
            guess_freq = self.freqs[max_ind]
            guess_height = max_height

            # Halt fitting process if candidate peak drops below minimum height.
            if not guess_height > self.min_peak_height:
                break

            # Data-driven first guess at standard deviation
            #  Find half height index on each side of the center frequency.
            half_height = 0.5 * max_height
            le_ind = next((x for x in range(max_ind - 1, 0, -1) if flat_iter[x] <= half_height), None)
            ri_ind = next((x for x in range(max_ind + 1, len(flat_iter), 1)
                           if flat_iter[x] <= half_height), None)

            # Keep bandwidth estimation from the shortest side.
            #  We grab shortest to avoid estimating very large std from overalapping peaks.
            # Grab the shortest side, ignoring a side if the half max was not found.
            #  Note: will fail if both le & ri ind's end up as None (probably shouldn't happen).
            shortest_side = min([abs(ind - max_ind) for ind in [le_ind, ri_ind] if ind is not None])

            # Estimate std from FWHM. Calculate FWHM, converting to Hz, get guess std from FWHM
            fwhm = shortest_side * 2 * self.freq_res
            guess_std = fwhm / (2 * np.sqrt(2 * np.log(2)))

            # Check that guess std isn't outside preset std limits; restrict if so.
            #  Note: without this, curve_fitting fails if given guess > or < bounds.
            if guess_std < self._gauss_std_limits[0]:
                guess_std = self._gauss_std_limits[0]
            if guess_std > self._gauss_std_limits[1]:
                guess_std = self._gauss_std_limits[1]

            # Collect guess parameters.
            guess = np.vstack((guess, (guess_freq, guess_height, guess_std)))

            # Subtract best-guess gaussian.
            peak_gauss = gaussian_function(self.freqs, guess_freq, guess_height, guess_std)
            flat_iter = flat_iter - peak_gauss

        # Check peaks based on edges, and on overlap
        #  Drop any that violate requirements.
        guess = self._drop_peak_cf(guess)
        guess = self._drop_peak_overlap(guess)

        # If there are peak guesses, fit the peaks, and sort results.
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

        # Set the bounds for center frequency, enforce positive height value, and set bandwidth limits.
        #  Note that 'guess' is in terms of gaussian standard deviation, so +/- BW is 2 * the guess_gauss_std.
        #  This set of list comprehensions is a way to end up with bounds in the form:
        #   ((cf_low_bound_peak1, height_low_bound_peak1, bw_low_bound_peak1, *repeated for n_peak*),
        #    (cf_high_bound_peak1, height_high_bound_peak1, bw_high_bound_peak, *repeated for n_peak*))
        lo_bound = [[peak[0] - 2 * self._cf_bound * peak[2], 0, self._gauss_std_limits[0]]
                    for peak in guess]
        hi_bound = [[peak[0] + 2 * self._cf_bound * peak[2], np.inf, self._gauss_std_limits[1]]
                    for peak in guess]

        # Check that CF bounds are within frequency range
        #   If they are  not, update them to be restricted to frequency range.
        lo_bound = [bound if bound[0] > self.freq_range[0] else \
            [self.freq_range[0], *bound[1:]] for bound in lo_bound]
        hi_bound = [bound if bound[0] < self.freq_range[1] else \
            [self.freq_range[1], *bound[1:]] for bound in hi_bound]

        # Unpacks the embedded lists into flat tuples
        #   This is what the fit function requires as input.
        gaus_param_bounds = (tuple([item for sublist in lo_bound for item in sublist]),
                             tuple([item for sublist in hi_bound for item in sublist]))

        # Flatten guess, for use with curve fit.
        guess = np.ndarray.flatten(guess)

        # Fit the peaks.
        gaussian_params, _ = curve_fit(gaussian_function, self.freqs, self._spectrum_flat,
                                       p0=guess, maxfev=5000, bounds=gaus_param_bounds)

        # Re-organize params into 2d matrix.
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
            Fitted parameter values for the peaks, with each row as [CF, PW, BW].

        Notes
        -----
        The gaussian center is unchanged as the peak center frequency.

        The gaussian height is updated to reflect the height of the peak above
        the aperiodic fit. This is returned instead of the gaussian height, as
        the gaussian height is harder to interpret, due to peak overlaps.

        The gaussian standard deviation is updated to be 'both-sided', to reflect the
        'bandwidth' of the peak, as opposed to the gaussian parameter, which is 1-sided.

        Performing this conversion requires that the model has been run,
        with `freqs`, `fooofed_spectrum_` and `ap_fit` all required to be available.
        """

        peak_params = np.empty([0, 3])

        for ii, peak in enumerate(gaus_params):

            # Gets the index of the power_spectrum at the frequency closest to the CF of the peak
            ind = min(range(len(self.freqs)), key=lambda ii: abs(self.freqs[ii] - peak[0]))

            # Collect peak parameter data
            peak_params = np.vstack((peak_params,
                                     [peak[0],
                                      self.fooofed_spectrum_[ind] - self._ap_fit[ind],
                                      peak[2] * 2]))

        return peak_params


    def _drop_peak_cf(self, guess):
        """Check whether to drop peaks based on center's proximity to the edge of the spectrum.

        Parameters
        ----------
        guess : 2d array, shape=[n_peaks, 3]
            Guess parameters for gaussian fits to peaks, as gaussian parameters.

        Returns
        -------
        guess : 2d array, shape=[n_peaks, 3]
            Guess parameters for gaussian fits to peaks, as gaussian parameters.
        """

        cf_params = [item[0] for item in guess]
        bw_params = [item[2] * self._bw_std_edge for item in guess]

        # Check if peaks within drop threshold from the edge of the frequency range.
        keep_peak = \
            (np.abs(np.subtract(cf_params, self.freq_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.freq_range[1])) > bw_params)

        # Drop peaks that fail the center frequency edge criterion
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _drop_peak_overlap(self, guess):
        """Checks whether to drop gaussians based on amount of overlap.

        Parameters
        ----------
        guess : 2d array, shape=[n_peaks, 3]
            Guess parameters for gaussian fits to peaks, as gaussian parameters.

        Returns
        -------
        guess : 2d array, shape=[n_peaks, 3]
            Guess parameters for gaussian fits to peaks, as gaussian parameters.

        Notes
        -----
        For any gaussians with an overlap that crosses the threshold,
        the lowest height guess guassian is dropped.
        """

        # Sort the peak guesses, so can check overlap of adjacent peaks
        guess = sorted(guess, key=lambda x: float(x[0]))

        # Calculate standard deviation bounds for checking amount of overlap
        bounds = [[peak[0] - peak[2] * self._gauss_overlap_thresh, peak[0],
                   peak[0] + peak[2] * self._gauss_overlap_thresh] for peak in guess]

        # Loop through peak bounds, comparing current bound to that of next peak
        drop_inds = []
        for ind, b_0 in enumerate(bounds[:-1]):
            b_1 = bounds[ind + 1]

            # Check if bound of current peak extends into next peak
            if b_0[1] > b_1[0]:

                # If so, get the index of the gaussian with the lowest height (to drop)
                drop_inds.append([ind, ind + 1][np.argmin([guess[ind][1], guess[ind + 1][1]])])

        # Drop any peaks guesses that overlap too much, based on threshold.
        keep_peak = [not ind in drop_inds for ind in range(len(guess))]
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _calc_r_squared(self):
        """Calculate R^2 of the full model fit."""

        r_val = np.corrcoef(self.power_spectrum, self.fooofed_spectrum_)
        self.r_squared_ = r_val[0][1] ** 2


    def _calc_rmse_error(self):
        """Calculate root mean squared error of the full model fit."""

        self.error_ = np.sqrt((self.power_spectrum - self.fooofed_spectrum_) ** 2).mean()


    @staticmethod
    def _prepare_data(freqs, power_spectrum, freq_range, spectra_dim=1, verbose=True):
        """Prepare input data for adding to FOOOF or FOOOFGroup object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear space.
        power_spectrum : 1d or 2d array
            Power values, which must be input in linear space.
            1d vector, or 2d as [n_power_spectra, n_freqs].
        freq_range : list of [float, float]
            Frequency range to restrict power spectrum to. If None, keeps the entire range.
        spectra_dim : int, optional default: 1
            Dimensionality that the power spectra should have.
        verbose : bool, optional
            Whether to be verbose in printing out warnings.

        Returns
        -------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear space.
        power_spectrum : 1d or 2d array
            Power spectrum values, in log10 scale.
            1d vector, or 2d as [n_power_specta, n_freqs].
        freq_range : list of [float, float]
            Minimum and maximum values of the frequency vector.
        freq_res : float
            Frequency resolution of the power spectrum.
        """

        # Check that data are the right types
        if not isinstance(freqs, np.ndarray) or not isinstance(power_spectrum, np.ndarray):
            raise ValueError('Input data must be numpy arrays.')

        # Check that data have the right dimensionality
        if freqs.ndim != 1 or (power_spectrum.ndim != spectra_dim):
            raise ValueError('Inputs are not the right dimensions.')

        # Check that data sizes are compatible
        if freqs.shape[-1] != power_spectrum.shape[-1]:
            raise ValueError('Inputs are not consistent size.')

        # Force data to be dtype of float64.
        #   If they end up as float32, or less, scipy curve_fit fails (sometimes implicitly)
        if freqs.dtype != 'float64':
            freqs = freqs.astype('float64')
        if power_spectrum.dtype != 'float64':
            power_spectrum = power_spectrum.astype('float64')

        # Check frequency range, trim the power_spectrum range if requested
        if freq_range:
            freqs, power_spectrum = trim_spectrum(freqs, power_spectrum, freq_range)
        else:
            freqs, power_spectrum = freqs, power_spectrum

        # Check if freqs start at 0 - move up one value if so.
        #   Aperiodic fit gets an inf is freq of 0 is included, which leads to an error.
        if freqs[0] == 0.0:
            freqs, power_spectrum = trim_spectrum(freqs, power_spectrum, [freqs[1], freqs.max()])
            if verbose:
                print("\nFOOOF WARNING: Skipping frequency == 0,"
                      " as this causes a problem with fitting.")

        # Calculate frequency resolution, and actual frequency range of the data
        freq_range = [freqs.min(), freqs.max()]
        freq_res = freqs[1] - freqs[0]

        # Log power values
        power_spectrum = np.log10(power_spectrum)

        return freqs, power_spectrum, freq_range, freq_res


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        # Reconstruct FOOOF object from loaded data
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
        #  This fixes an issue where they end up the wrong shape if they are empty (no peaks)
        if set(get_obj_desc()['results']).issubset(set(data.keys())):
            self.peak_params_ = check_array_dim(self.peak_params_)
            self._gaussian_params = check_array_dim(self._gaussian_params)


    def _check_loaded_settings(self, data):
        """Check if settings added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If settings not loaded from file, clear from object, so that default
        #  settings, which are potentially wrong for loaded data, aren't kept
        if not set(get_obj_desc()['settings']).issubset(set(data.keys())):

            # Reset all public settings to None
            for setting in get_obj_desc()['settings']:
                setattr(self, setting, None)

            # Infer whether knee fitting was used, if aperiodic params have been loaded
            if np.all(self.aperiodic_params_):
                self.aperiodic_mode = infer_ap_func(self.aperiodic_params_)

        # Reset internal settings so that they are consistent with what was loaded
        #  Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _regenerate_freqs(self):
        """Regenerate the frequency vector, given the object metadata."""

        self.freqs = gen_freqs(self.freq_range, self.freq_res)


    def _regenerate_model(self):
        """Regenerate model fit from parameters."""

        self._ap_fit = gen_aperiodic(self.freqs, self.aperiodic_params_)
        self._peak_fit = gen_peaks(self.freqs, np.ndarray.flatten(self._gaussian_params))
        self.fooofed_spectrum_ = self._peak_fit + self._ap_fit
