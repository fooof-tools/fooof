"""FOOOF - Fitting Oscillations & One-Over F.

Notes
-----
- Methods without defined docstrings import docs at runtime, from aliased external functions.
- Private attributes of the FOOOF method, not publicly exposed, are documented below.

Attributes (private)
----------
_psd_flat : 1d array
    Flattened PSD (background 1/f removed)
_psd_osc_rm : 1d array
    PSD with oscillations removed (not flattened).
_gaussian_params : 2d array
    Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].
_background_fit : 1d array
    Values of the background fit.
_oscillation_fit : 1d array
    Values of the oscillation fit (flattened).
_bg_amp_thresh : float
    Noise threshold for finding oscillations above the background.
_bg_guess : list of [float, float, float]
    Guess parameters for fitting background.
_bg_bounds : tuple of tuple of float
    Upper and lower bounds on fitting background.
_bw_std_edge : float
    Banwidth threshold for edge rejection of oscillations, units of standard deviation.
_std_limits : list of [float, float]
    Bandwidth limits, converted to use for gaussian standard deviation parameter.
_bg_fit_func : function
    Function used to fit the background.
"""

import warnings
from collections import namedtuple

import numpy as np
from scipy.optimize import curve_fit

from fooof.utils import trim_psd, mk_freq_vector
from fooof.plts.fm import plot_fm
from fooof.core.io import save_fm, load_json
from fooof.core.reports import create_report_fm
from fooof.core.funcs import gaussian_function, expo_function, expo_nk_function
from fooof.core.utils import group_three, check_array_dim
from fooof.core.modutils import get_obj_desc, docs_drop_param
from fooof.core.strings import gen_settings_str, gen_results_str_fm, gen_report_str, gen_bw_warn_str

###################################################################################################
###################################################################################################

FOOOFResult = namedtuple('FOOOFResult', ['background_params', 'oscillation_params',
                                         'r2', 'error', 'gaussian_params'])

class FOOOF(object):
    """Model the physiological power spectrum as oscillatory peaks and 1/f background.

    WARNING: FOOOF expects frequency and power values in linear space.
        Passing in logged frequencies and/or power spectra is not detected,
            and will silently produce incorrect results.

    Parameters
    ----------
    bandwidth_limits : tuple of (float, float), optional (default: (0.5, 12.0)
        Setting to exclude gaussian fits where the bandwidth is implausibly narrow or wide.
    max_n_gauss : int, optional (default: inf)
        Maximum number of oscillations to be modeled in a single PSD.
    min_amp : float, optional (default: 0)
        Minimum amplitude threshold for an oscillation to be modeled.
    amp_std_thresh : float, optional (default: 2.0)
        Amplitude threshold for detecting oscillatory peaks, units of standard deviation.
    bg_use_knee : boolean, optional (default: False)
        Whether to fit a knee parameter when fitting the background.
    verbose : boolean, optional (default: True)
        Whether to be verbose in printing out warnings.

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the PSD.
    psd : 1d array
        Input power spectral density values.
    freq_range : list of [float, float]
        Frequency range of the PSD.
    freq_res : float
        Frequency resolution of the PSD.
    psd_fit_ : 1d array
        The full model fit of the PSD: 1/f and oscillations across freq_range.
    background_params_ : 1d array
        Parameters that define the background fit.
    oscillation_params_ : 2d array
        Fitted parameter values for the oscillations. Each row is an oscillation, as [CF, Amp, BW].
    r2_ : float
        R-squared between the input PSD and the full model fit.
    error_ : float
        R-squared error of the full model fit.

    Notes
    -----
    Input PSDs should be smooth - overly noisy power spectra may lead to bad fits.
    - In particular, raw FFT inputs are not appropriate, we recommend using either Welch's
      procedure, or a median filter smoothing on the FFT output before running FOOOF.
    - Where possible and appropriate, use longer time segments for PSD calculation to
      get smoother PSDs, as this will give better FOOOF fits.
    """

    def __init__(self, bandwidth_limits=(0.5, 12.0), max_n_gauss=np.inf,
                 min_amp=0.0, amp_std_thresh=2.0, bg_use_knee=False, verbose=True):
        """Initialize FOOOF object with run parameters."""

        # Set input parameters
        self.bg_use_knee = bg_use_knee
        self.bandwidth_limits = bandwidth_limits
        self.max_n_gauss = max_n_gauss
        self.min_amp = min_amp
        self.amp_std_thresh = amp_std_thresh
        self.verbose = verbose

        ## SETTINGS - these are updateable by the user if required.
        # Noise threshold, as a percentage of the lowest amplitude values in the total data to fit.
        #  Defines the minimum amplitude, above residuals, to be considered an oscillation.
        self._bg_amp_thresh = 0.025
        # Guess parameters for background fitting, [offset, knee, slope]
        #  If offset guess is None, the first value of the PSD is used as offset guess
        self._bg_guess = [None, 0, 2]
        # Bounds for background fitting, as: ((offset_low_bound, knee_low_bound, sl_low_bound),
        #                                     (offset_high_bound, knee_high_bound, sl_high_bound))
        #  By default, background fitting is unbound, but can be restricted here, if desired
        #    Even if fitting without knee, leave bounds for knee (they are dropped later)
        self._bg_bounds = ((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf))
        # Threshold for how far (units of gaus std dev) an oscillation has to be from edge to keep.
        self._bw_std_edge = 1.0
        # Parameter bounds for center frequency when fitting gaussians - in terms of +/- std dev
        self._cf_bound = 1.5

        # Initialize internal settings and data attributes (to None)
        self._reset_settings()
        self._reset_data()


    def _reset_settings(self):
        """Set (or reset) internal settings, based on what is provided in init.

        Notes
        -----
        These settings are for interal use, based on what is provided to, or set in init.
            They should not be altered by the user.
        """

        # Set exponential function version for whether fitting knee or not
        self._bg_fit_func = expo_function if self.bg_use_knee else expo_nk_function

        # Only update these settings if other relevant settings are available
        #   Otherwise, assume settings are unknown (have been cleared) and leave as None
        if self.bandwidth_limits:

            # Bandwidth limits are given in 2-sided oscillation bandwidth.
            #  Convert to gaussian std parameter limits.
            self._std_limits = [bwl / 2 for bwl in self.bandwidth_limits]
            # Bounds for background fitting. Drops bounds on knee parameter if not set to fit knee
            self._bg_bounds = self._bg_bounds if self.bg_use_knee \
                else tuple(bound[0::2] for bound in self._bg_bounds)


    def _reset_data(self, clear_freqs=True):
        """Set (or reset) all data attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional
            Whether to clear frequency information too.
        """

        if clear_freqs:
            self.freqs = None
            self.freq_range = None
            self.freq_res = None

        self.psd = None
        self.psd_fit_ = None
        self.background_params_ = None
        self.oscillation_params_ = None
        self.r2_ = None
        self.error_ = None

        self._psd_flat = None
        self._psd_osc_rm = None
        self._gaussian_params = None
        self._background_fit = None
        self._oscillation_fit = None


    def add_data(self, freqs, psd, freq_range=None):
        """Add data (frequencies and PSD values) to FOOOF object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear space.
        psd : 1d array
            Power spectral density values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict PSD to. If not provided, keeps the entire range.
        """

        if freqs.ndim != psd.ndim != 1:
            raise ValueError('Inputs are not the right dimensions.')

        self.freqs, self.psd, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, psd, freq_range, self.verbose)


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
        self.oscillation_params_ = fooof_result.oscillation_params
        self.r2_ = fooof_result.r2
        self.error_ = fooof_result.error
        self._gaussian_params = fooof_result.gaussian_params

        if regenerate:
            self._regenerate_model()


    def model(self, freqs=None, psd=None, freq_range=None, plt_log=False):
        """Run model fit, plot, and print results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the PSD.
        psd : 1d array, optional
            Power spectral density values.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        plt_log : boolean, optional
            Whether or not to plot the frequency axis in log space. default: False

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        self.fit(freqs, psd, freq_range)
        self.plot(plt_log)
        self.print_results()


    def fit(self, freqs=None, psd=None, freq_range=None):
        """Fit the full PSD as 1/f and gaussian oscillations.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the PSD, in linear space.
        psd : 1d array, optional
            Power spectral density values, in linear space.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.

        Notes
        -----
        Data is optional if data has been already been added to FOOOF object.
        """

        # If freqs & psd provided together, add data to object.
        if isinstance(freqs, np.ndarray) and isinstance(psd, np.ndarray):
            self.add_data(freqs, psd, freq_range)
        # If PSD provided alone, add to object, and use existing frequency data
        #  Note: be careful passing in PSD data like this:
        #    It assumes the PSD is already logged, with correct freq_range.
        elif isinstance(psd, np.ndarray):
            self.psd = psd

        # Check that data is available
        if not (np.all(self.freqs) and np.all(self.psd)):
            raise ValueError('No data available to fit - can not proceed.')

        # Check and warn about bandwidth limits (if in verbose mode)
        if self.verbose:
            self._check_bw()

        # Fit the background 1/f.
        self.background_params_ = self._clean_background_fit(self.freqs, self.psd)
        self._background_fit = self._create_bg_fit(self.freqs, self.background_params_)

        # Flatten the PSD using fit background.
        self._psd_flat = self.psd - self._background_fit

        # Find oscillations, and fit them with gaussians.
        self._gaussian_params = self._fit_oscs(np.copy(self._psd_flat))

        # Calculate the oscillation fit.
        #  Note: if no oscillations are found, this creates a flat (all zero) oscillation fit.
        self._oscillation_fit = self._create_osc_fit(self.freqs, self._gaussian_params)

        # Create oscillation-removed (but not flattened) PSD.
        self._psd_osc_rm = self.psd - self._oscillation_fit

        # Run final background fit on oscillation-removed PSD.
        #   Note: This overwrites previous background fit.
        self.background_params_ = self._quick_background_fit(self.freqs, self._psd_osc_rm)
        self._background_fit = self._create_bg_fit(self.freqs, self.background_params_)

        # Create full PSD model fit.
        self.psd_fit_ = self._oscillation_fit + self._background_fit

        # Convert gaussian definitions to oscillation parameters
        self.oscillation_params_ = self._create_osc_params(self._gaussian_params)

        # Calculate R^2 and error of the model fit.
        self._r_squared()
        self._rmse_error()


    def print_settings(self, description=False):
        """Print out the current FOOOF settings.

        Parameters
        ----------
        description : bool, optional (default: True)
            Whether to print out a description with current settings.
        """

        print(gen_settings_str(self, description))


    def print_results(self):
        """Print out FOOOF results."""

        print(gen_results_str_fm(self))


    @staticmethod
    def print_report_issue():
        """Prints instructions on how to report bugs and/or problematic fits."""

        print(gen_report_str())


    def get_results(self):
        """Return model fit parameters and error."""

        return FOOOFResult(self.background_params_, self.oscillation_params_, self.r2_,
                           self.error_, self._gaussian_params)


    def plot(self, plt_log=False, save_fig=False, file_name='FOOOF_fit', file_path='', ax=None):

        plot_fm(self, plt_log, save_fig, file_name, file_path, ax)


    def create_report(self, file_name='FOOOF_Report', file_path='', plt_log=False):

        create_report_fm(self, file_name, file_path, plt_log)


    def save(self, file_name='fooof_data', file_path='', append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fm(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name='fooof_data', file_path=''):
        """Load in FOOOF file. Reads in a JSON file.

        Parameters
        ----------
        file_name : str or FileObject, optional
            File from which to load data.
        file_path : str
            Path to directory from which to load. If not provided, loads from current directory.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data()

        # Load JSON file, add to self and check loaded data
        data = load_json(file_name, file_path)
        self._add_from_dict(data)
        self._check_loaded_settings(data)
        self._check_loaded_results(data)


    def _check_bw(self):
        """Check and warn about bandwidth limits / frequency resolution interaction."""

        # Check bandwidth limits against frequency resolution; warn if too close.
        if 1.5 * self.freq_res >= self.bandwidth_limits[0]:
            print(gen_bw_warn_str(self.freq_res, self.bandwidth_limits[0]))


    def _check_loaded_results(self, data, regenerate=True):
        """Check if results added, check data, and regenerate model, if requested.

        Parameters
        ----------
        data : dict
            The dictionary of data that has been added to the object.
        regenerate : bool, optional
            Whether to regenerate the PSD model. default : True
        """

        # If results loaded, check dimensions of osc/gauss parameters
        #  This fixes an issue where they end up the wrong shape if they are empty (no oscs)
        if set(get_obj_desc()['results']).issubset(set(data.keys())):
            self.oscillation_params_ = check_array_dim(self.oscillation_params_)
            self._gaussian_params = check_array_dim(self._gaussian_params)

        # Regenerate PSD model & components
        if regenerate:
            if np.all(self.freqs) and np.all(self.background_params_):
                self._regenerate_model()


    def _quick_background_fit(self, freqs, psd):
        """Fit the 1/f background of PSD using a lorentzian fit.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear scale.
        psd : 1d array
            Power spectral density values, in log10 scale.

        Returns
        -------
        background_params : 1d array of [offset, knee, slope]
            Parameter estimates for background fit. Only includes knee if set to fit knee.
        """

        # Set guess params for lorentzian background fit, guess params set at init
        guess = np.array(([psd[0]] if not self._bg_guess[0] else [self._bg_guess[0]]) +
                         ([self._bg_guess[1]] if self.bg_use_knee else []) +
                         [self._bg_guess[2]])

        # Ignore warnings that are raised in curve_fit
        #  A runtime warning can occur while exploring parameters in curve fitting
        #    This doesn't effect outcome - it won't settle on an answer that does this
        #  It happens if / when b < 0 & |b| > x**2, as it leads to log of a negative number
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            background_params, _ = curve_fit(self._bg_fit_func, freqs, psd, p0=guess,
                                             maxfev=5000, bounds=self._bg_bounds)

        return background_params


    def _clean_background_fit(self, freqs, psd):
        """Fit the 1/f background of PSD using an lorentzian fit, ignoring outliers.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear scale.
        psd : 1d array
            Power spectral density values, in log10 scale.

        Returns
        -------
        background_params : 1d array of [offset, knee, slope]
            Parameter estimates for background fit. Only includes knee if set to fit knee.
        """

        # Do a quick, initial background fit.
        popt = self._quick_background_fit(freqs, psd)
        initial_fit = self._create_bg_fit(freqs, popt)

        # Flatten PSD based on initial background fit.
        psd_flat = psd - initial_fit

        # Flatten outliers - any points that drop below 0.
        psd_flat[psd_flat < 0] = 0

        # Amplitude threshold - in terms of # of points.
        perc_thresh = np.percentile(psd_flat, self._bg_amp_thresh)
        amp_mask = psd_flat <= perc_thresh
        f_ignore = freqs[amp_mask]
        psd_ignore = psd[amp_mask]

        # Second background fit - using results of first fit as guess parameters.
        #  See note in _quick_background_fit about warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            background_params, _ = curve_fit(self._bg_fit_func, f_ignore, psd_ignore,
                                             p0=popt, maxfev=5000, bounds=self._bg_bounds)

        return background_params


    def _create_bg_fit(self, freqs, bg_params):
        """Generate the fit of the background component of the PSD.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear scale.
        bg_params : 1d array
            Parameters that define the background fit.

        Returns
        -------
        1d array
            Values of the background fit.
        """

        return self._bg_fit_func(freqs, *bg_params)


    @staticmethod
    def _create_osc_fit(freqs, gaus_params):
        """Generate the fit of the oscillations component of the PSD.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear scale.
        gaus_params : 2d array
            Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].

        Returns
        -------
        1d array
            Values of the oscillation fit.
        """

        return gaussian_function(freqs, *np.ndarray.flatten(gaus_params))


    def _fit_oscs(self, flat_iter):
        """Iteratively fit oscillations to flattened spectrum.

        Parameters
        ----------
        flat_iter : 1d array
            Flattened PSD values.

        Returns
        -------
        gaussian_params : 2d array
            Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].
        """

        # Initialize matrix of guess parameters for gaussian fitting.
        guess = np.empty([0, 3])

        # Find oscillations: Loop through, checking residuals, stopping based on std check
        while len(guess) < self.max_n_gauss:

            # Find candidate oscillation.
            max_ind = np.argmax(flat_iter)
            max_amp = flat_iter[max_ind]

            # Stop searching for oscillations peaks once drops below amplitude threshold.
            if max_amp <= self.amp_std_thresh * np.std(flat_iter):
                break

            # Set the guess parameters for gaussian fitting - CF and amp.
            guess_freq = self.freqs[max_ind]
            guess_amp = max_amp

            # Halt fitting process if candidate osc drops below minimum amp size.
            if not guess_amp > self.min_amp:
                break

            # Data-driven first guess BW
            #  Find half-amp index on each side of the center frequency.
            half_amp = 0.5 * max_amp
            le_ind = next((x for x in range(max_ind - 1, 0, -1) if flat_iter[x] <= half_amp), None)
            ri_ind = next((x for x in range(max_ind + 1, len(flat_iter), 1)
                           if flat_iter[x] <= half_amp), None)

            # Keep bandwidth estimation from the shortest side.
            #  We grab shortest to avoid estimating very large std from overalapping oscillations.
            # Grab the shortest side, ignoring a side if the half max was not found.
            #  Note: will fail if both le & ri ind's end up as None (probably shouldn't happen).
            shortest_side = min([abs(ind - max_ind) for ind in [le_ind, ri_ind] if ind is not None])

            # Estimate std from FWHM. Calculate FWHM, converting to Hz, get guess std from FWHM
            fwhm = shortest_side * 2 * self.freq_res
            guess_std = fwhm / (2 * np.sqrt(2 * np.log(2)))

            # Check that guess std isn't outside preset std limits; restrict if so.
            #  Note: without this, curve_fitting fails if given guess > or < bounds.
            if guess_std < self._std_limits[0]:
                guess_std = self._std_limits[0]
            if guess_std > self._std_limits[1]:
                guess_std = self._std_limits[1]

            # Collect guess parameters.
            guess = np.vstack((guess, (guess_freq, guess_amp, guess_std)))

            # Subtract best-guess gaussian.
            osc_gauss = gaussian_function(self.freqs, guess_freq, guess_amp, guess_std)
            flat_iter = flat_iter - osc_gauss

        # Check oscillations based on edges, and on overlap
        #  Drop any that violate requirements.
        guess = self._drop_osc_cf(guess)
        guess = self._drop_osc_overlap(guess)

        # If there are oscillation guesses, fit the oscillations, and sort results.
        if len(guess) > 0:
            gaussian_params = self._fit_osc_guess(guess)
            gaussian_params = gaussian_params[gaussian_params[:, 0].argsort()]
        else:
            gaussian_params = np.array([])

        return gaussian_params


    def _fit_osc_guess(self, guess):
        """Fit a guess of oscillaton gaussian fit.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, amp, BW].

        Returns
        -------
        gaussian_params : 2d array
            Parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, amp, BW].
        """

        # Set the bounds for center frequency, positive amp value, and gauss limits.
        #  Note that osc_guess is in terms of gaussian std, so +/- BW is 2 * the guess_gauss_std.
        #  This set of list comprehensions is a way to end up with bounds in the form:
        #   ((cf_low_bound_osc1, amp_low_bound_osc1, bw_low_bound_osc1, *repeated for n oscs*),
        #    (cf_high_bound_osc1, amp_high_bound_osc1, bw_high_bound_osc1, *repeated for n oscs*))
        lo_bound = [[osc[0] - 2 * self._cf_bound * osc[2], 0, self._std_limits[0]]
                    for osc in guess]
        hi_bound = [[osc[0] + 2 * self._cf_bound * osc[2], np.inf, self._std_limits[1]]
                    for osc in guess]
        # The double for-loop here unpacks the embedded lists
        gaus_param_bounds = (tuple([item for sublist in lo_bound for item in sublist]),
                             tuple([item for sublist in hi_bound for item in sublist]))

        # Flatten guess, for use with curve fit.
        guess = np.ndarray.flatten(guess)

        # Fit the oscillations.
        gaussian_params, _ = curve_fit(gaussian_function, self.freqs, self._psd_flat,
                                       p0=guess, maxfev=5000, bounds=gaus_param_bounds)

        # Re-organize params into 2d matrix.
        gaussian_params = np.array(group_three(gaussian_params))

        return gaussian_params


    def _create_osc_params(self, gaus_params):
        """Copies over the gaussian params to oscillation outputs, updating as appropriate.

        Parameters
        ----------
        gaus_params :  2d array
            Parameters that define the gaussian fit(s).
                Each row is a gaussian, as [mean, amp, std].

        Returns
        -------
        oscillation_params :  2d array
            Fitted parameter values for the oscillations.
                Each row is an oscillation, as [CF, Amp, BW].

        Notes
        -----
        Amplitude is updated to the amplitude of oscillation above the background fit.
          - This is returned instead of the gaussian amplitude
            - Gaussian amplitude is harder to interpret, due to osc overlaps.
        Bandwidth is updated to be 'both-sided'
          - This is as opposed to gaussian std param, which is 1-sided.
        Performing this conversion requires that the model be run.
          - In particular, freqs, psd_fit and _background_fit are required to be available.
        """

        oscillation_params = np.empty([0, 3])

        for ii, osc in enumerate(gaus_params):

            # Gets the index of the PSD at the frequency closest to the CF of the osc
            ind = min(range(len(self.freqs)), key=lambda ii: abs(self.freqs[ii] - osc[0]))

            # Collect oscillation parameter data
            oscillation_params = np.vstack((oscillation_params,
                                            [osc[0],
                                             self.psd_fit_[ind] - self._background_fit[ind],
                                             osc[2] * 2]))

        return oscillation_params


    def _drop_osc_cf(self, guess):
        """Check whether to drop oscillations based CF proximity to edge.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, amp, BW].

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, amp, BW].
        """

        cf_params = [item[0] for item in guess]
        bw_params = [item[2] * self._bw_std_edge for item in guess]

        # Check if oscs within 1 BW (std dev) of the edge.
        keep_osc = \
            (np.abs(np.subtract(cf_params, self.freq_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.freq_range[1])) > bw_params)

        # Drop oscillations that fail CF edge criterion
        guess = np.array([d for (d, keep) in zip(guess, keep_osc) if keep])

        return guess


    def _drop_osc_overlap(self, guess):
        """Checks whether to drop oscillations based on overlap.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, amp, BW].

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, amp, BW].

        Notes
        -----
        For any oscillation guesses with an overlap of their standard deviations,
            only the large oscillation guess is kept.
        """

        # Sort the oscillations guesses, so can check overlap of adjacent oscillations
        guess = sorted(guess, key=lambda x: float(x[0]))

        # Calculate standard deviation bounds
        bounds = [[osc[0] - osc[2], osc[0], osc[0] + osc[2]] for osc in guess]

        drop_inds = []

        # Loop through oscillation bounds, comparing current bound to that of next osc
        for ind, b_0 in enumerate(bounds[:-1]):
            b_1 = bounds[ind + 1]

            # Check if bound of current oscillations extends into next oscillation
            if b_0[1] > b_1[0]:

                # If so, get the index of the lowest amplitude oscillation (to drop)
                drop_inds.append([ind, ind + 1][np.argmin([guess[ind][1], guess[ind + 1][1]])])

        # Drop any oscillations guesses that overlap
        keep_osc = [True if j not in drop_inds else False for j in range(len(guess))]
        guess = np.array([d for (d, keep) in zip(guess, keep_osc) if keep])

        return guess


    def _r_squared(self):
        """Calculate R^2 of the full model fit."""

        r_val = np.corrcoef(self.psd, self.psd_fit_)
        self.r2_ = r_val[0][1] ** 2


    def _rmse_error(self):
        """Calculate root mean squared error of the full model fit."""

        self.error_ = np.sqrt((self.psd - self.psd_fit_) ** 2).mean()


    @staticmethod
    def _prepare_data(freqs, psd, freq_range, verbose=True):
        """Prepare input data for adding to FOOOF or FOOOFGroup object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, in linear space.
        psd : 1d or 2d array
            Power values, in linear space. Either 1d vector, or 2d as [n_psds, n_freqs].
        freq_range :
            Frequency range to restrict PSD to. If None, keeps the entire range.
        verbose : bool, optional
            Whether to be verbose in printing out warnings.

        Returns
        -------
        freqs : 1d array
            Frequency values for the PSD, in linear space.
        psd : 1d or 2d array
            Power values, in linear space. Either 1d vector, or 2d as [n_psds, n_freqs].
        freq_range : list of [float, float]
            Frequency range - minimum and maximum values of the frequency vector.
        freq_res : float
            Frequency resolution of the PSD.
        """

        if freqs.shape[-1] != psd.shape[-1]:
            raise ValueError('Inputs are not consistent size.')

        # Check frequency range, trim the PSD range if requested
        if freq_range:
            freqs, psd = trim_psd(freqs, psd, freq_range)
        else:
            freqs, psd = freqs, psd

        # Check if freqs start at 0 - move up one value if so.
        #   Background fit gets an inf is freq of 0 is included, which leads to an error.
        if freqs[0] == 0.0:
            freqs, psd = trim_psd(freqs, psd, [freqs[1], freqs.max()])
            if verbose:
                print("\nFOOOF WARNING: Skipping frequency == 0,"
                      " as this causes problem with fitting.")

        # Calculate frequency resolution, and actual frequency range of the data
        freq_range = [freqs.min(), freqs.max()]
        freq_res = freqs[1] - freqs[0]

        # Log power values
        psd = np.log10(psd)

        return freqs, psd, freq_range, freq_res


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
            self.freqs = mk_freq_vector(self.freq_range, self.freq_res)


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
            self._clear_settings()

            # Infer whether knee fitting was used, if background params have been loaded
            if np.all(self.background_params_):
                self._infer_knee()

        # Otherwise (settings were loaded), reset internal settings so that they are consistent
        else:
            self._reset_settings()


    def _clear_settings(self):
        """Clears all setting for current instance, setting them all to None."""

        for setting in get_obj_desc()['all_settings']:
            setattr(self, setting, None)


    def _infer_knee(self):
        """Infer from background params, whether knee fitting was used, and update settings."""

        #  Given results, can tell which function was used from the length of bg_params
        if len(self.background_params_) == 3:
            self.bg_use_knee = True
            self._bg_fit_func = expo_function
        else:
            self.bg_use_knee = False
            self._bg_fit_func = expo_nk_function


    def _regenerate_model(self):
        """Regenerate model fit from parameters."""

        self._background_fit = self._create_bg_fit(self.freqs, self.background_params_)
        self._oscillation_fit = self._create_osc_fit(self.freqs, self._gaussian_params)
        self.psd_fit_ = self._oscillation_fit + self._background_fit


# DOCS: Copy over docs for an aliased functions to the method docstrings
for func_name in get_obj_desc()['alias_funcs']:
    getattr(FOOOF, func_name).__doc__ = \
        docs_drop_param(eval(func_name + '_' + 'fm').__doc__)
