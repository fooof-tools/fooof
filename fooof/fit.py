"""FOOOF - Fitting Oscillations & One-Over F.

Notes
-----
- Methods without defined docstrings import docs at runtime, from aliased external functions.
- Private attributes of the FOOOF method, not publicly exposed, are documented below.

Attributes (private)
----------
_spectrum_flat : 1d array
    Flattened power spectrum (background 1/f removed)
_spectrum_peak_rm : 1d array
    Power spectrum with peaks removed (not flattened).
_gaussian_params : 2d array
    Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].
_bg_fit : 1d array
    Values of the background fit.
_peak_fit : 1d array
    Values of the peak fit (flattened).
_bg_amp_thresh : float
    Noise threshold for finding peaks above the background.
_bg_guess : list of [float, float, float]
    Guess parameters for fitting background.
_bg_bounds : tuple of tuple of float
    Upper and lower bounds on fitting background.
_bw_std_edge : float
    Bandwidth threshold for edge rejection of peaks, in units of gaussian std. deviation.
_gauss_overlap_thresh : float
    Degree of overlap (in units of guassian std. deviation) between gaussian guesses to drop one.
_gauss_std_limits : list of [float, float]
    Peak width limits, converted to use for gaussian standard deviation parameter.
"""

import warnings
from copy import deepcopy
from collections import namedtuple

import numpy as np
from scipy.optimize import curve_fit

from fooof.utils import trim_spectrum
from fooof.plts.fm import plot_fm
from fooof.core.io import save_fm, load_json
from fooof.core.reports import save_report_fm
from fooof.core.funcs import gaussian_function, get_bg_func, infer_bg_func
from fooof.core.utils import group_three, check_array_dim
from fooof.core.modutils import get_obj_desc, copy_doc_func_to_method
from fooof.core.strings import gen_settings_str, gen_results_str_fm, gen_issue_str, gen_wid_warn_str

from fooof.synth import gen_freqs, gen_background, gen_peaks

###################################################################################################
###################################################################################################

FOOOFResult = namedtuple('FOOOFResult', ['background_params', 'peak_params',
                                         'r_squared', 'error', 'gaussian_params'])
FOOOFResult.__doc__ = """\
The resulting parameters and associated data of a FOOOF model fit.

Attributes
----------
background_params : 1d array, len 2 or 3
    Parameters that define the background fit. As [Intercept, (Knee), Slope].
        The knee parameter is only included if background fit with knee. Otherwise, length is 2.
peak_params : 2d array, shape=[n_peaks, 3]
    Fitted parameter values for the peaks. Each row is a peak, as [CF, Amp, BW].
r_squared : float
    R-squared of the fit between the input power spectrum and the full model fit.
error : float
    Root mean squared error of the full model fit.
gaussian_params : 2d array, shape=[n_peaks, 3]
    Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].
"""

class FOOOF(object):
    """Model the physiological power spectrum as a combination of 1/f background and peaks.

    WARNING: FOOOF expects frequency and power values in linear space.
        Passing in logged frequencies and/or power spectra is not detected,
            and will silently produce incorrect results.

    Parameters
    ----------
    peak_width_limits : tuple of (float, float), optional
        Limits on possible peak width, as [lower_bound, upper_bound]. default: [0.5, 12.0]
    max_n_peaks : int, optional
        Maximum number of gaussians to be fit in a single spectrum. default: inf
    min_peak_amplitude : float, optional
        Minimum amplitude threshold for a peak to be modeled. default: 0
    peak_threshold : float, optional
        Threshold for detecting peaks, units of standard deviation. default: 2.0
    background_mode : {'fixed', 'knee'}
        Which approach to take to fitting the background.
    verbose : boolean, optional
        Whether to be verbose in printing out warnings. default: True

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the power spectrum.
    power_spectrum : 1d array
        Power spectrum values.
    freq_range : list of [float, float]
        Frequency range of the power spectrum.
    freq_res : float
        Frequency resolution of the power spectrum.
    fooofed_spectrum_ : 1d array
        The full model fit of the power spectrum: background and peaks across freq_range.
    background_params_ : 1d array
        Parameters that define the background fit. As [Intercept, (Knee), Slope].
                The knee parameter is only included if background fit with knee.
    peak_params_ : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CF, Amp, BW].
    r_squared_ : float
        R-squared of the fit between the input power spectrum and the full model fit.
    error_ : float
        Root mean squared error of the full model fit.

    Notes
    -----
    Input power spectra should be smooth - overly noisy power spectra may lead to bad fits.
    - In particular, raw FFT inputs are not appropriate, we recommend using either Welch's
      procedure, or a median filter smoothing on the FFT output before running FOOOF.
    - Where possible and appropriate, use longer time segments for power spectrum calculation to
      get smoother power spectra, as this will give better FOOOF fits.
    """

    def __init__(self, peak_width_limits=[0.5, 12.0], max_n_peaks=np.inf, min_peak_amplitude=0.0,
                 peak_threshold=2.0, background_mode='fixed', verbose=True):
        """Initialize FOOOF object with run parameters."""

        # Double check correct scipy version is being used
        from scipy import __version__
        major, minor, _ = __version__.split('.')
        if int(major) < 1 and int(minor) < 19:
            raise ImportError('Scipy version of >= 0.19.0 required.')

        # Set input parameters
        self.background_mode = background_mode
        self.peak_width_limits = peak_width_limits
        self.max_n_peaks = max_n_peaks
        self.min_peak_amplitude = min_peak_amplitude
        self.peak_threshold = peak_threshold
        self.verbose = verbose

        ## SETTINGS - these are updateable by the user if required.
        # Noise threshold, as a percentage of the lowest amplitude values in the total data to fit.
        #  Defines the minimum amplitude, above residuals, to be considered a peak.
        self._bg_amp_thresh = 0.025
        # Guess parameters for background fitting, [offset, knee, slope]
        #  If offset guess is None, the first value of the power spectrum is used as offset guess
        self._bg_guess = [None, 0, 2]
        # Bounds for background fitting, as: ((offset_low_bound, knee_low_bound, sl_low_bound),
        #                                     (offset_high_bound, knee_high_bound, sl_high_bound))
        #  By default, background fitting is unbound, but can be restricted here, if desired
        #    Even if fitting without knee, leave bounds for knee (they are dropped later)
        self._bg_bounds = ((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf))
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
        These settings are for interal use, based on what is provided to, or set in init.
            They should not be altered by the user.
        """

        # Only update these settings if other relevant settings are available
        if self.peak_width_limits:

            # Bandwidth limits are given in 2-sided peak bandwidth.
            #  Convert to gaussian std parameter limits.
            self._gauss_std_limits = [bwl / 2 for bwl in self.peak_width_limits]
            # Bounds for background fitting. Drops bounds on knee parameter if not set to fit knee
            self._bg_bounds = self._bg_bounds if self.background_mode == 'knee' \
                else tuple(bound[0::2] for bound in self._bg_bounds)

        # Otherwise, assume settings are unknown (have been cleared) and set to None
        else:
            self._gauss_std_limits = None
            self._bg_bounds = None


    def _reset_data_results(self, clear_freqs=True, clear_spectrum=True, clear_results=True):
        """Set (or reset) data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional
            Whether to clear frequency attributes.
        clear_power_spectrum : bool, optional
            Whether to clear power spectrum attribute.
        clear_results : bool, optional
            Whether to clear model results attributes.
        """

        if clear_freqs:
            self.freqs = None
            self.freq_range = None
            self.freq_res = None

        if clear_spectrum:
            self.power_spectrum = None

        if clear_results:
            self.fooofed_spectrum_ = None
            self.background_params_ = np.array([np.nan, np.nan]) if \
                self.background_mode == 'fixed' else np.array([np.nan, np.nan, np.nan])
            self.peak_params_ = np.array([np.nan, np.nan, np.nan])
            self.r_squared_ = np.nan
            self.error_ = np.nan

            self._spectrum_flat = None
            self._spectrum_peak_rm = None
            self._gaussian_params = np.array([np.nan, np.nan, np.nan])
            self._bg_fit = None
            self._peak_fit = None


    def add_data(self, freqs, power_spectrum, freq_range=None):
        """Add data (frequencies and power spectrum values) to FOOOF object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array
            Power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to. If not provided, keeps the entire range.
        """

        self.freqs, self.power_spectrum, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, power_spectrum, freq_range, 1, self.verbose)


    def add_results(self, fooof_result, regenerate=False):
        """Add results data back into object from a FOOOFResult object.

        Parameters
        ----------
        fooof_result : FOOOFResult
            An object containing the results from fitting a FOOOF model.
        regenerate : bool, optional
            Whether to regenerate the model fits from the given fit parameters. default : False
        """

        self.background_params_ = fooof_result.background_params
        self.peak_params_ = fooof_result.peak_params
        self.r_squared_ = fooof_result.r_squared
        self.error_ = fooof_result.error
        self._gaussian_params = fooof_result.gaussian_params

        if regenerate:
            self._regenerate_model()


    def report(self, freqs=None, power_spectrum=None, freq_range=None, plt_log=False):
        """Run model fit, and display a report, which includes a plot, and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum.
        power_spectrum : 1d array, optional
            Power spectral density values.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        plt_log : boolean, optional
            Whether or not to plot the frequency axis in log space. default: False

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        self.fit(freqs, power_spectrum, freq_range)
        self.plot(plt_log)
        self.print_results(False)


    def fit(self, freqs=None, power_spectrum=None, freq_range=None):
        """Fit the full power spectrum as a combination of background and peaks.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array, optional
            Power spectrum values, in linear space.
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

            # Fit the background 1/f.
            self.background_params_ = self._robust_bg_fit(self.freqs, self.power_spectrum)
            self._bg_fit = gen_background(self.freqs, self.background_params_)

            # Flatten the power_spectrum using fit background.
            self._spectrum_flat = self.power_spectrum - self._bg_fit

            # Find peaks, and fit them with gaussians.
            self._gaussian_params = self._fit_peaks(np.copy(self._spectrum_flat))

            # Calculate the peak fit.
            #  Note: if no peaks are found, this creates a flat (all zero) peak fit.
            self._peak_fit = gen_peaks(self.freqs, np.ndarray.flatten(self._gaussian_params))

            # Create peak-removed (but not flattened) power spectrum.
            self._spectrum_peak_rm = self.power_spectrum - self._peak_fit

            # Run final background fit on peak-removed power spectrum.
            #   Note: This overwrites previous background fit.
            self.background_params_ = self._simple_bg_fit(self.freqs, self._spectrum_peak_rm)
            self._bg_fit = gen_background(self.freqs, self.background_params_)

            # Create full power_spectrum model fit.
            self.fooofed_spectrum_ = self._peak_fit + self._bg_fit

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
        description : bool, optional
            Whether to print out a description with current settings. default: False
        concise : bool, optional
            Whether to print the report in a concise mode, or not. default: False
        """

        print(gen_settings_str(self, description, concise))


    def print_results(self, concise=False):
        """Print out FOOOF results.

        Parameters
        ----------
        concise : bool, optional
            Whether to print the report in a concise mode, or not. default: False
        """

        print(gen_results_str_fm(self, concise))


    @staticmethod
    def print_report_issue(concise=False):
        """Prints instructions on how to report bugs and/or problematic fits.

        Parameters
        ----------
        concise : bool, optional
            Whether to print the report in a concise mode, or not. default: False
        """

        print(gen_issue_str(concise))


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics."""

        return FOOOFResult(self.background_params_, self.peak_params_, self.r_squared_,
                           self.error_, self._gaussian_params)


    @copy_doc_func_to_method(plot_fm)
    def plot(self, plt_log=False, save_fig=False, file_name='FOOOF_fit', file_path='', ax=None):

        plot_fm(self, plt_log, save_fig, file_name, file_path, ax)


    @copy_doc_func_to_method(save_report_fm)
    def save_report(self, file_name='FOOOF_Report', file_path='', plt_log=False):

        save_report_fm(self, file_name, file_path, plt_log)


    @copy_doc_func_to_method(save_fm)
    def save(self, file_name='fooof_data', file_path='', append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fm(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name='fooof_data', file_path=''):
        """Load in FOOOF file. Reads in a JSON file.

        Parameters
        ----------
        file_name : str or FileObject, optional
            File from which to load data.
        file_path : str, optional
            Path to directory from which to load. If not provided, loads from current directory.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data_results()

        # Load JSON file, add to self and check loaded data
        data = load_json(file_name, file_path)
        self._add_from_dict(data)
        self._check_loaded_settings(data)
        self._check_loaded_results(data)


    def copy(self):
        """Return a copy of the FOOOF object."""

        return deepcopy(self)


    def _check_width_limits(self):
        """Check and warn about peak width limits / frequency resolution interaction."""

        # Check peak width limits against frequency resolution; warn if too close.
        if 1.5 * self.freq_res >= self.peak_width_limits[0]:
            print(gen_wid_warn_str(self.freq_res, self.peak_width_limits[0]))


    def _check_loaded_results(self, data, regenerate=True):
        """Check if results added, check data, and regenerate model, if requested.

        Parameters
        ----------
        data : dict
            The dictionary of data that has been added to the object.
        regenerate : bool, optional
            Whether to regenerate the power_spectrum model. default : True
        """

        # If results loaded, check dimensions of peak parameters
        #  This fixes an issue where they end up the wrong shape if they are empty (no peaks)
        if set(get_obj_desc()['results']).issubset(set(data.keys())):
            self.peak_params_ = check_array_dim(self.peak_params_)
            self._gaussian_params = check_array_dim(self._gaussian_params)

        # Regenerate power_spectrum model & components
        if regenerate:
            if np.all(self.freqs) and np.all(self.background_params_):
                self._regenerate_model()


    def _simple_bg_fit(self, freqs, power_spectrum):
        """Fit the 1/f background of power spectrum.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear scale.
        power_spectrum : 1d array
            Power spectrum values, in log10 scale.

        Returns
        -------
        background_params : 1d array
            Parameter estimates for background fit.
        """

        # Set guess params for lorentzian background fit, guess params set at init
        guess = np.array(([power_spectrum[0]] if not self._bg_guess[0] else [self._bg_guess[0]]) +
                         ([self._bg_guess[1]] if self.background_mode == 'knee' else []) +
                         [self._bg_guess[2]])

        # Ignore warnings that are raised in curve_fit
        #  A runtime warning can occur while exploring parameters in curve fitting
        #    This doesn't effect outcome - it won't settle on an answer that does this
        #  It happens if / when b < 0 & |b| > x**2, as it leads to log of a negative number
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            background_params, _ = curve_fit(get_bg_func(self.background_mode),
                                             freqs, power_spectrum, p0=guess,
                                             maxfev=5000, bounds=self._bg_bounds)

        return background_params


    def _robust_bg_fit(self, freqs, power_spectrum):
        """Fit the 1/f background of power spectrum robustly, ignoring outliers.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectrum, in linear scale.
        power_spectrum : 1d array
            Power spectrum values, in log10 scale.

        Returns
        -------
        background_params : 1d array
            Parameter estimates for background fit.
        """

        # Do a quick, initial background fit.
        popt = self._simple_bg_fit(freqs, power_spectrum)
        initial_fit = gen_background(freqs, popt)

        # Flatten power_spectrum based on initial background fit.
        flatspec = power_spectrum - initial_fit

        # Flatten outliers - any points that drop below 0.
        flatspec[flatspec < 0] = 0

        # Amplitude threshold - in terms of # of points.
        perc_thresh = np.percentile(flatspec, self._bg_amp_thresh)
        amp_mask = flatspec <= perc_thresh
        freqs_ignore = freqs[amp_mask]
        spectrum_ignore = power_spectrum[amp_mask]

        # Second background fit - using results of first fit as guess parameters.
        #  See note in _simple_bg_fit about warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            background_params, _ = curve_fit(get_bg_func(self.background_mode),
                                             freqs_ignore, spectrum_ignore, p0=popt,
                                             maxfev=5000, bounds=self._bg_bounds)

        return background_params


    def _fit_peaks(self, flat_iter):
        """Iteratively fit peaks to flattened spectrum.

        Parameters
        ----------
        flat_iter : 1d array
            Flattened power spectrum values.

        Returns
        -------
        gaussian_params : 2d array
            Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].
        """

        # Initialize matrix of guess parameters for gaussian fitting.
        guess = np.empty([0, 3])

        # Find peak: Loop through, finding a candidate peak, and fitting with a guass gaussian.
        #  Stopping procedure based on either # of peaks, or the threshold/amplitude limits.
        while len(guess) < self.max_n_peaks:

            # Find candidate peak - the maximum point of the flattened spectrum.
            max_ind = np.argmax(flat_iter)
            max_amp = flat_iter[max_ind]

            # Stop searching for peaks peaks once drops below amplitude threshold.
            if max_amp <= self.peak_threshold * np.std(flat_iter):
                break

            # Set the guess parameters for gaussian fitting - CF and amp.
            guess_freq = self.freqs[max_ind]
            guess_amp = max_amp

            # Halt fitting process if candidate peak drops below minimum amp size.
            if not guess_amp > self.min_peak_amplitude:
                break

            # Data-driven first guess BW
            #  Find half-amp index on each side of the center frequency.
            half_amp = 0.5 * max_amp
            le_ind = next((x for x in range(max_ind - 1, 0, -1) if flat_iter[x] <= half_amp), None)
            ri_ind = next((x for x in range(max_ind + 1, len(flat_iter), 1)
                           if flat_iter[x] <= half_amp), None)

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
            guess = np.vstack((guess, (guess_freq, guess_amp, guess_std)))

            # Subtract best-guess gaussian.
            peak_gauss = gaussian_function(self.freqs, guess_freq, guess_amp, guess_std)
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
        guess : 2d array
            Guess parameters for gaussian fits to peaks. [n_peaks, 3], row: [CF, amp, BW].

        Returns
        -------
        gaussian_params : 2d array
            Parameters for gaussian fits to peaks. [n_peaks, 3], row: [CF, amp, BW].
        """

        # Set the bounds for center frequency, enforce positive amp value, and set bandwidth limits.
        #  Note that 'guess' is in terms of gaussian std, so +/- BW is 2 * the guess_gauss_std.
        #  This set of list comprehensions is a way to end up with bounds in the form:
        #   ((cf_low_bound_peak1, amp_low_bound_peak1, bw_low_bound_peak1, *repeated for n_peak*),
        #    (cf_high_bound_peak1, amp_high_bound_peak1, bw_high_bound_peak, *repeated for n_peak*))
        lo_bound = [[peak[0] - 2 * self._cf_bound * peak[2], 0, self._gauss_std_limits[0]]
                    for peak in guess]
        hi_bound = [[peak[0] + 2 * self._cf_bound * peak[2], np.inf, self._gauss_std_limits[1]]
                    for peak in guess]

        # Check that CF bounds are within frequency range, and, if not, updates them to be restricted to frequency range.
        lo_bound = [bound if bound[0] > self.freq_range[0] else [self.freq_range[0], *bound[1:]] for bound in lo_bound]
        hi_bound = [bound if bound[0] < self.freq_range[1] else [self.freq_range[1], *bound[1:]] for bound in hi_bound]

        # Unpacks the embedded lists into flat tuples, which is what the fit function requires as input.
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
        gaus_params :  2d array
            Parameters that define the gaussian fit(s).
                Each row is a gaussian, as [mean, amp, std].

        Returns
        -------
        peak_params :  2d array
            Fitted parameter values for the peaks.
                Each row is a peak, as [CF, Amp, BW].

        Notes
        -----
        Amplitude is updated to the amplitude of peak above the background fit.
          - This is returned instead of the gaussian amplitude
            - Gaussian amplitude is harder to interpret, due to peak overlaps.
        Bandwidth is updated to be 'both-sided'
          - This is as opposed to gaussian std param, which is 1-sided.
        Performing this conversion requires that the model be run.
          - In particular, freqs, fooofed_spectrum and _bg_fit are required to be available.
        """

        peak_params = np.empty([0, 3])

        for ii, peak in enumerate(gaus_params):

            # Gets the index of the power_spectrum at the frequency closest to the CF of the peak
            ind = min(range(len(self.freqs)), key=lambda ii: abs(self.freqs[ii] - peak[0]))

            # Collect peak parameter data
            peak_params = np.vstack((peak_params,
                                     [peak[0],
                                      self.fooofed_spectrum_[ind] - self._bg_fit[ind],
                                      peak[2] * 2]))

        return peak_params


    def _drop_peak_cf(self, guess):
        """Check whether to drop peaks based CF proximity to edge.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to peaks. [n_peaks, 3], row: [CF, amp, BW].

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to peaks. [n_peaks, 3], row: [CF, amp, BW].
        """

        cf_params = [item[0] for item in guess]
        bw_params = [item[2] * self._bw_std_edge for item in guess]

        # Check if peaks within drop threshold from the edge of the frequency range.
        keep_peak = \
            (np.abs(np.subtract(cf_params, self.freq_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.freq_range[1])) > bw_params)

        # Drop peaks that fail CF edge criterion
        guess = np.array([d for (d, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _drop_peak_overlap(self, guess):
        """Checks whether to drop peaks based on overlap.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to peaks. [n_peaks, 3], row: [CF, amp, BW].

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to peaks. [n_peaks, 3], row: [CF, amp, BW].

        Notes
        -----
        For any peak guesses with an overlap that crosses threshold,
            the lower amplitude guess is dropped.
        """

        # Sort the peak guesses, so can check overlap of adjacent peaks
        guess = sorted(guess, key=lambda x: float(x[0]))

        # Calculate standard deviation bounds for checking amount of overlap
        bounds = [[peak[0] - peak[2] * self._gauss_overlap_thresh, peak[0],
                   peak[0] + peak[2] * self._gauss_overlap_thresh] for peak in guess]

        drop_inds = []

        # Loop through peak bounds, comparing current bound to that of next peak
        for ind, b_0 in enumerate(bounds[:-1]):
            b_1 = bounds[ind + 1]

            # Check if bound of current peak extends into next peak
            if b_0[1] > b_1[0]:

                # If so, get the index of the lowest amplitude peak (to drop)
                drop_inds.append([ind, ind + 1][np.argmin([guess[ind][1], guess[ind + 1][1]])])

        # Drop any peaks guesses that overlap too much, based on threshold.
        keep_peak = [True if j not in drop_inds else False for j in range(len(guess))]
        guess = np.array([d for (d, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _calc_r_squared(self):
        """Calculate R^2 of the full model fit."""

        r_val = np.corrcoef(self.power_spectrum, self.fooofed_spectrum_)
        self.r_squared_ = r_val[0][1] ** 2


    def _calc_rmse_error(self):
        """Calculate root mean squared error of the full model fit."""

        self.error_ = np.sqrt((self.power_spectrum - self.fooofed_spectrum_) ** 2).mean()


    @staticmethod
    def _prepare_data(freqs, power_spectrum, freq_range, psd_dim=1, verbose=True):
        """Prepare input data for adding to FOOOF or FOOOFGroup object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear space.
        power_spectrum : 1d or 2d array
            Power spectrum values, in linear space. 1d vector, or 2d as [n_power_spectra, n_freqs].
        freq_range : list of [float, float]
            Frequency range to restrict power spectrum to. If None, keeps the entire range.
        psd_dim : int, optional default: 1
            Dimensionality that the power_spectrum should have.
        verbose : bool, optional
            Whether to be verbose in printing out warnings.

        Returns
        -------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear space.
        power_spectrum : 1d or 2d array
            Power spectrum values, in linear space. 1d vector, or 2d as [n_power_specta, n_freqs].
        freq_range : list of [float, float]
            Minimum and maximum values of the frequency vector.
        freq_res : float
            Frequency resolution of the power spectrum.
        """

        # Check that data are the right types
        if not isinstance(freqs, np.ndarray) or not isinstance(power_spectrum, np.ndarray):
            raise ValueError('Input data must be numpy arrays.')

        # Check that data have the right dimensionality
        if freqs.ndim != 1 or (power_spectrum.ndim != psd_dim):
            raise ValueError('Inputs are not the right dimensions.')

        # Check that data sizes are compatible
        if freqs.shape[-1] != power_spectrum.shape[-1]:
            raise ValueError('Inputs are not consistent size.')

        # Check frequency range, trim the power_spectrum range if requested
        if freq_range:
            freqs, power_spectrum = trim_spectrum(freqs, power_spectrum, freq_range)
        else:
            freqs, power_spectrum = freqs, power_spectrum

        # Check if freqs start at 0 - move up one value if so.
        #   Background fit gets an inf is freq of 0 is included, which leads to an error.
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

        # Reconstruct frequency vector, if data available to do so
        if self.freq_res:
            self.freqs = gen_freqs(self.freq_range, self.freq_res)


    def _check_loaded_settings(self, data):
        """Check if settings added, and update the object as needed.

        Parameters
        ----------
        data : dict
            The dictionary of data that has been added to the object.
        """

        # If settings not loaded from file, clear from object, so that default
        #  settings, which are potentially wrong for loaded data, aren't kept
        if not set(get_obj_desc()['settings']).issubset(set(data.keys())):

            # Reset all public settings to None
            for setting in get_obj_desc()['settings']:
                setattr(self, setting, None)

            # Infer whether knee fitting was used, if background params have been loaded
            if np.all(self.background_params_):
                self.background_mode = infer_bg_func(self.background_params_)

        # Reset internal settings so that they are consistent with what was loaded
        #  Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _regenerate_model(self):
        """Regenerate model fit from parameters."""

        self._bg_fit = gen_background(self.freqs, self.background_params_)
        self._peak_fit = gen_peaks(self.freqs, np.ndarray.flatten(self._gaussian_params))
        self.fooofed_spectrum_ = self._peak_fit + self._bg_fit
