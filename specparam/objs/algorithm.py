"""Define spectral fitting algorithm object."""

import warnings

import numpy as np
from numpy.linalg import LinAlgError
from scipy.optimize import curve_fit

from specparam.utils.select import groupby
from specparam.core.funcs import gaussian_function, get_ap_func
from specparam.core.jacobians import jacobian_gauss
from specparam.reports.strings import gen_width_warning_str
from specparam.modutils.errors import NoDataError, FitError
from specparam.measures.params import compute_gauss_std
from specparam.sim.gen import gen_aperiodic, gen_periodic

###################################################################################################
###################################################################################################

class SpectralFitAlgorithm():
    """Base object defining model & algorithm for spectral parameterization.

    Parameters
    ----------
    % public settings described in `SpectralModel`
    _ap_percentile_thresh : float
        Percentile threshold, to select points from a flat spectrum for an initial aperiodic fit
        Points are selected at a low percentile value to restrict to non-peak points.
    _ap_guess : list of [float, float, float]
        Guess parameters for fitting the aperiodic component, as [offset, knee, exponent].
        If offset guess is None, the first value of the power spectrum is used as offset guess
        If exponent guess is None, the abs(log-log slope) of first & last points is used
    _ap_bounds : tuple of tuple of float
        Bounds for aperiodic fitting, as: ((offset_low_bound, knee_low_bound, exp_low_bound),
                                           (offset_high_bound, knee_high_bound, exp_high_bound))
        By default, aperiodic fitting is unbound, but can be restricted here.
        Even if fitting without knee, leave bounds for knee (they are dropped later).
    _cf_bound : float
        Parameter bounds for center frequency when fitting gaussians, in terms of +/- std dev.
    _bw_std_edge : float
        Threshold for how far a peak has to be from edge to keep.
        This is defined in units of gaussian standard deviation.
    _gauss_overlap_thresh : float
        Degree of overlap between gaussian guesses for one to be dropped.
        This is defined in units of gaussian standard deviation.
    _maxfev : int
        The maximum number of calls to the curve fitting function.
    _tol : float
        The tolerance setting for curve fitting (see scipy.curve_fit - ftol / xtol / gtol).
        The default value reduce tolerance to speed fitting (as compared to curve_fit's default).
        Set value to 1e-8 to match curve_fit default
    _error_metric : str
        The error metric to use for post-hoc measures of model fit error.
        Note: this is for checking error post fitting, not an objective function for fitting.
        See `_calc_error` for options.
    _debug : bool
        Run mode: whether the object is set in debug mode.
        If in debug mode, an error is raised if model fitting is unsuccessful.
        This should be controlled by using the `set_debug_mode` method.

    Attributes
    ----------
    _gauss_std_limits : list of [float, float]
        Settings attribute: peak width limits, to use for gaussian standard deviation parameter.
        This attribute is computed based on `peak_width_limits` and should not be updated directly.
    _spectrum_flat : 1d array
        Data attribute: flattened power spectrum, with the aperiodic component removed.
    _spectrum_peak_rm : 1d array
        Data attribute: power spectrum, with peaks removed.
    _ap_fit : 1d array
        Model attribute: values of the isolated aperiodic fit.
    _peak_fit : 1d array
        Model attribue: values of the isolated peak fit.
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, peak_width_limits=(0.5, 12.0), max_n_peaks=np.inf, min_peak_height=0.0,
                 peak_threshold=2.0, ap_percentile_thresh=0.025,  ap_guess=(None, 0, None),
                 ap_bounds=((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf)),
                 cf_bound=1.5, bw_std_edge=1.0, gauss_overlap_thresh=0.75,
                 maxfev=5000, tol=0.00001):
        """Initialize base model object"""

        ## Public settings
        self.peak_width_limits = peak_width_limits
        self.max_n_peaks = max_n_peaks
        self.min_peak_height = min_peak_height
        self.peak_threshold = peak_threshold

        ## Private settings: model parameters related settings
        self._ap_percentile_thresh = ap_percentile_thresh
        self._ap_guess = ap_guess
        self._ap_bounds = ap_bounds
        self._cf_bound = cf_bound
        self._bw_std_edge = bw_std_edge
        self._gauss_overlap_thresh = gauss_overlap_thresh

        ## Private setting: curve_fit relates settings
        self._maxfev = maxfev
        self._tol = tol

        ## Set internal settings, based on inputs, and initialize data & results attributes
        self._reset_internal_settings()
        self._reset_data_results(True, True, True)


    def _fit(self, freqs=None, power_spectrum=None, freq_range=None):
        """Define the full fitting algorithm."""

        # If freqs & power_spectrum provided together, add data to object.
        if freqs is not None and power_spectrum is not None:
            self.add_data(freqs, power_spectrum, freq_range)
        # If power spectrum provided alone, add to object, and use existing frequency data
        #   Note: be careful passing in power_spectrum data like this:
        #     It assumes the power_spectrum is already logged, with correct freq_range
        elif isinstance(power_spectrum, np.ndarray):
            self.power_spectrum = power_spectrum

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
                if np.any(np.isinf(self.power_spectrum)) or np.any(np.isnan(self.power_spectrum)):
                    raise FitError("Model fitting was skipped because there are NaN or Inf "
                                   "values in the data, which preclude model fitting.")

            # Fit the aperiodic component
            self.aperiodic_params_ = self._robust_ap_fit(self.freqs, self.power_spectrum)
            self._ap_fit = gen_aperiodic(self.freqs, self.aperiodic_params_)

            # Flatten the power spectrum using fit aperiodic fit
            self._spectrum_flat = self.power_spectrum - self._ap_fit

            # Find peaks, and fit them with gaussians
            self.gaussian_params_ = self._fit_peaks(np.copy(self._spectrum_flat))

            # Calculate the peak fit
            #   Note: if no peaks are found, this creates a flat (all zero) peak fit
            self._peak_fit = gen_periodic(self.freqs, np.ndarray.flatten(self.gaussian_params_))

            # Create peak-removed (but not flattened) power spectrum
            self._spectrum_peak_rm = self.power_spectrum - self._peak_fit

            # Run final aperiodic fit on peak-removed power spectrum
            #   This overwrites previous aperiodic fit, and recomputes the flattened spectrum
            self.aperiodic_params_ = self._simple_ap_fit(self.freqs, self._spectrum_peak_rm)
            self._ap_fit = gen_aperiodic(self.freqs, self.aperiodic_params_)
            self._spectrum_flat = self.power_spectrum - self._ap_fit

            # Create full power_spectrum model fit
            self.modeled_spectrum_ = self._peak_fit + self._ap_fit

            # Convert gaussian definitions to peak parameters
            self.peak_params_ = self._create_peak_params(self.gaussian_params_)

            # Calculate R^2 and error of the model fit
            self._calc_r_squared()
            self._calc_error()

        except FitError:

            # If in debug mode, re-raise the error
            if self._debug:
                raise

            # Clear any interim model results that may have run
            #   Partial model results shouldn't be interpreted in light of overall failure
            self._reset_results(clear_results=True)

            # Print out status
            if self.verbose:
                print("Model fitting was unsuccessful.")


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


    # ToCheck: this currently overrides basefit
    #   Once modes are used, this can be dropped (I think)
    def _reset_results(self, clear_results=False):
        """Set, or reset, results attributes to empty.

        Parameters
        ----------
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        if clear_results:

            self.aperiodic_params_ = np.array([np.nan] * \
                (2 if self.aperiodic_mode == 'fixed' else 3))
            self.gaussian_params_ = np.empty([0, 3])
            self.peak_params_ = np.empty([0, 3])
            self.r_squared_ = np.nan
            self.error_ = np.nan

            self.modeled_spectrum_ = None

            self._spectrum_flat = None
            self._spectrum_peak_rm = None
            self._ap_fit = None
            self._peak_fit = None


    def _check_width_limits(self):
        """Check and warn about peak width limits / frequency resolution interaction."""

        # Check peak width limits against frequency resolution and warn if too close
        if 1.5 * self.freq_res >= self.peak_width_limits[0]:
            print(gen_width_warning_str(self.freq_res, self.peak_width_limits[0]))


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

        # Get the guess parameters and/or calculate from the data, as needed
        #   Note that these are collected as lists, to concatenate with or without knee later
        off_guess = [power_spectrum[0] if not self._ap_guess[0] else self._ap_guess[0]]
        kne_guess = [self._ap_guess[1]] if self.aperiodic_mode == 'knee' else []
        exp_guess = [np.abs((self.power_spectrum[-1] - self.power_spectrum[0]) /
                            (np.log10(self.freqs[-1]) - np.log10(self.freqs[0])))
                     if not self._ap_guess[2] else self._ap_guess[2]]

        # Get bounds for aperiodic fitting, dropping knee bound if not set to fit knee
        ap_bounds = self._ap_bounds if self.aperiodic_mode == 'knee' \
            else tuple(bound[0::2] for bound in self._ap_bounds)

        # Collect together guess parameters
        guess = np.array(off_guess + kne_guess + exp_guess)

        # Ignore warnings that are raised in curve_fit
        #   A runtime warning can occur while exploring parameters in curve fitting
        #     This doesn't effect outcome - it won't settle on an answer that does this
        #   It happens if / when b < 0 & |b| > x**2, as it leads to log of a negative number
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                aperiodic_params, _ = curve_fit(get_ap_func(self.aperiodic_mode),
                                                freqs, power_spectrum, p0=guess,
                                                maxfev=self._maxfev, bounds=ap_bounds,
                                                ftol=self._tol, xtol=self._tol, gtol=self._tol,
                                                check_finite=False)
        except RuntimeError as excp:
            error_msg = ("Model fitting failed due to not finding parameters in "
                         "the simple aperiodic component fit.")
            raise FitError(error_msg) from excp

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

        Raises
        ------
        FitError
            If the fitting encounters an error.
        """

        # Do a quick, initial aperiodic fit
        popt = self._simple_ap_fit(freqs, power_spectrum)
        initial_fit = gen_aperiodic(freqs, popt)

        # Flatten power_spectrum based on initial aperiodic fit
        flatspec = power_spectrum - initial_fit

        # Flatten outliers, defined as any points that drop below 0
        flatspec[flatspec < 0] = 0

        # Use percentile threshold, in terms of # of points, to extract and re-fit
        perc_thresh = np.percentile(flatspec, self._ap_percentile_thresh)
        perc_mask = flatspec <= perc_thresh
        freqs_ignore = freqs[perc_mask]
        spectrum_ignore = power_spectrum[perc_mask]

        # Get bounds for aperiodic fitting, dropping knee bound if not set to fit knee
        ap_bounds = self._ap_bounds if self.aperiodic_mode == 'knee' \
            else tuple(bound[0::2] for bound in self._ap_bounds)

        # Second aperiodic fit - using results of first fit as guess parameters
        #  See note in _simple_ap_fit about warnings
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                aperiodic_params, _ = curve_fit(get_ap_func(self.aperiodic_mode),
                                                freqs_ignore, spectrum_ignore, p0=popt,
                                                maxfev=self._maxfev, bounds=ap_bounds,
                                                ftol=self._tol, xtol=self._tol, gtol=self._tol,
                                                check_finite=False)
        except RuntimeError as excp:
            error_msg = ("Model fitting failed due to not finding "
                         "parameters in the robust aperiodic fit.")
            raise FitError(error_msg) from excp
        except TypeError as excp:
            error_msg = ("Model fitting failed due to sub-sampling "
                         "in the robust aperiodic fit.")
            raise FitError(error_msg) from excp

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

        # Initialize matrix of guess parameters for gaussian fitting
        guess = np.empty([0, 3])

        # Find peak: Loop through, finding a candidate peak, and fitting with a guess gaussian
        #   Stopping procedures: limit on # of peaks, or relative or absolute height thresholds
        while len(guess) < self.max_n_peaks:

            # Find candidate peak - the maximum point of the flattened spectrum
            max_ind = np.argmax(flat_iter)
            max_height = flat_iter[max_ind]

            # Stop searching for peaks once height drops below height threshold
            if max_height <= self.peak_threshold * np.std(flat_iter):
                break

            # Set the guess parameters for gaussian fitting, specifying the mean and height
            guess_freq = self.freqs[max_ind]
            guess_height = max_height

            # Halt fitting process if candidate peak drops below minimum height
            if not guess_height > self.min_peak_height:
                break

            # Data-driven first guess at standard deviation
            #   Find half height index on each side of the center frequency
            half_height = 0.5 * max_height
            le_ind = next((val for val in range(max_ind - 1, 0, -1)
                           if flat_iter[val] <= half_height), None)
            ri_ind = next((val for val in range(max_ind + 1, len(flat_iter), 1)
                           if flat_iter[val] <= half_height), None)

            # Guess bandwidth procedure: estimate the width of the peak
            try:
                # Get an estimated width from the shortest side of the peak
                #   We grab shortest to avoid estimating very large values from overlapping peaks
                # Grab the shortest side, ignoring a side if the half max was not found
                short_side = min([abs(ind - max_ind) \
                    for ind in [le_ind, ri_ind] if ind is not None])

                # Use the shortest side to estimate full-width, half max (converted to Hz)
                #   and use this to estimate that guess for gaussian standard deviation
                fwhm = short_side * 2 * self.freq_res
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
            guess = np.vstack((guess, (guess_freq, guess_height, guess_std)))
            peak_gauss = gaussian_function(self.freqs, guess_freq, guess_height, guess_std)
            flat_iter = flat_iter - peak_gauss

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

        # Set the bounds for CF, enforce positive height value, and set bandwidth limits
        #   Note that 'guess' is in terms of gaussian std, so +/- BW is 2 * the guess_gauss_std
        #   This set of list comprehensions is a way to end up with bounds in the form:
        #     ((cf_low_peak1, height_low_peak1, bw_low_peak1, *repeated for n_peaks*),
        #      (cf_high_peak1, height_high_peak1, bw_high_peak, *repeated for n_peaks*))
        #     ^where each value sets the bound on the specified parameter
        lo_bound = [[peak[0] - 2 * self._cf_bound * peak[2], 0, self._gauss_std_limits[0]]
                    for peak in guess]
        hi_bound = [[peak[0] + 2 * self._cf_bound * peak[2], np.inf, self._gauss_std_limits[1]]
                    for peak in guess]

        # Check that CF bounds are within frequency range
        #   If they are  not, update them to be restricted to frequency range
        lo_bound = [bound if bound[0] > self.freq_range[0] else \
            [self.freq_range[0], *bound[1:]] for bound in lo_bound]
        hi_bound = [bound if bound[0] < self.freq_range[1] else \
            [self.freq_range[1], *bound[1:]] for bound in hi_bound]

        # Unpacks the embedded lists into flat tuples
        #   This is what the fit function requires as input
        gaus_param_bounds = (tuple(item for sublist in lo_bound for item in sublist),
                             tuple(item for sublist in hi_bound for item in sublist))

        # Flatten guess, for use with curve fit
        guess = np.ndarray.flatten(guess)

        # Fit the peaks
        try:
            gaussian_params, _ = curve_fit(gaussian_function, self.freqs, self._spectrum_flat,
                                           p0=guess, maxfev=self._maxfev, bounds=gaus_param_bounds,
                                           ftol=self._tol, xtol=self._tol, gtol=self._tol,
                                           check_finite=False, jac=jacobian_gauss)
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
        gaussian_params = np.array(groupby(gaussian_params, 3))

        return gaussian_params


    def _drop_peak_cf(self, guess):
        """Check whether to drop peaks based on center's proximity to the edge of the spectrum.

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

        # Check if peaks within drop threshold from the edge of the frequency range
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

        # Sort the peak guesses by increasing frequency
        #   This is so adjacent peaks can be compared from right to left
        guess = sorted(guess, key=lambda x: float(x[0]))

        # Calculate standard deviation bounds for checking amount of overlap
        #   The bounds are the gaussian frequency +/- gaussian standard deviation
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
        with `freqs`, `modeled_spectrum_` and `_ap_fit` all required to be available.
        """

        peak_params = np.empty((len(gaus_params), 3))

        for ii, peak in enumerate(gaus_params):

            # Gets the index of the power_spectrum at the frequency closest to the CF of the peak
            ind = np.argmin(np.abs(self.freqs - peak[0]))

            # Collect peak parameter data
            peak_params[ii] = [peak[0], self.modeled_spectrum_[ind] - self._ap_fit[ind],
                               peak[2] * 2]

        return peak_params
