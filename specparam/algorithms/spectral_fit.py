"""Define original spectral fitting algorithm object."""

import warnings

import numpy as np
from numpy.linalg import LinAlgError
from scipy.optimize import curve_fit

from specparam.modutils.errors import FitError
from specparam.utils.select import groupby
from specparam.reports.strings import gen_width_warning_str
from specparam.measures.params import compute_gauss_std
from specparam.algorithms.algorithm import Algorithm
from specparam.algorithms.settings import SettingsDefinition

###################################################################################################
###################################################################################################

SPECTRAL_FIT_SETTINGS = SettingsDefinition({
    'peak_width_limits' : {
        'type' : 'tuple of (float, float), optional, default: (0.5, 12.0)',
        'description' : 'Limits on possible peak width, in Hz, as (lower_bound, upper_bound).',
        },
    'max_n_peaks' : {
        'type' : 'int, optional, default: inf',
        'description' : 'Maximum number of peaks to fit.',
        },
    'min_peak_height' : {
        'type' : 'float, optional, default: 0',
        'description' : \
            'Absolute threshold for detecting peaks.\n        ' \
            'This threshold is defined in absolute units of the power spectrum (log power).',
        },
    'peak_threshold' : {
        'type' : 'float, optional, default: 2.0',
        'description' : \
            'Relative threshold for detecting peaks.\n        ' \
            'Threshold is defined in relative units of the power spectrum (standard deviation).',
        },
})


class SpectralFitAlgorithm(Algorithm):
    """Base object defining model & algorithm for spectral parameterization.

    Parameters
    ----------
    % public settings described in Spectral Fit Algorithm Settings
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
        Set value to 1e-8 to match curve_fit default.

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
        Model attribute: values of the isolated peak fit.
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, peak_width_limits=(0.5, 12.0), max_n_peaks=np.inf, min_peak_height=0.0,
                 peak_threshold=2.0, ap_percentile_thresh=0.025, ap_guess=None, ap_bounds=None,
                 cf_bound=1.5, bw_std_edge=1.0, gauss_overlap_thresh=0.75,
                 maxfev=5000, tol=0.00001,
                 modes=None, data=None, results=None, debug=False, verbose=False):
        """Initialize base model object"""

        # Initialize base algorithm object with algorithm metadata
        super().__init__(
            name='spectral fit',
            description='Original parameterizing neural power spectra algorithm.',
            settings=SPECTRAL_FIT_SETTINGS, format='spectrum',
            modes=modes, data=data, results=results, debug=debug)

        ## Public settings
        self.peak_width_limits = peak_width_limits
        self.max_n_peaks = max_n_peaks
        self.min_peak_height = min_peak_height
        self.peak_threshold = peak_threshold

        ## Private settings: model parameters related settings
        self._ap_percentile_thresh = ap_percentile_thresh
        self._ap_guess = ap_guess
        self._set_ap_bounds(ap_bounds)
        self._cf_bound = cf_bound
        self._bw_std_edge = bw_std_edge
        self._gauss_overlap_thresh = gauss_overlap_thresh

        ## Private setting: curve_fit related settings
        self._maxfev = maxfev
        self._tol = tol

        ## Set internal settings, based on inputs, and initialize data & results attributes
        self._reset_internal_settings()


    def _fit_prechecks(self, verbose=True):
        """Prechecks to run before the fit function.

        Notes
        -----
        Checks peak width limits and raises a warning if lower limit is too
        low given the frequency resolution of the data.
        """

        if verbose:
            if 1.5 * self.data.freq_res >= self.peak_width_limits[0]:
                print(gen_width_warning_str(self.data.freq_res, self.peak_width_limits[0]))


    def _fit(self):
        """Define the full fitting algorithm."""

        ## FIT PROCEDURES

        # Take an initial fit of the aperiodic component
        temp_aperiodic_params_ = self._robust_ap_fit(self.data.freqs, self.data.power_spectrum)
        temp_ap_fit = self.modes.aperiodic.func(self.data.freqs, *temp_aperiodic_params_)

        # Find peaks from the flattened power spectrum, and fit them with gaussians
        temp_spectrum_flat = self.data.power_spectrum - temp_ap_fit
        self.results.gaussian_params_ = self._fit_peaks(temp_spectrum_flat)

        # Calculate the peak fit
        #   Note: if no peaks are found, this creates a flat (all zero) peak fit
        self.results._peak_fit = self.modes.periodic.func(\
            self.data.freqs, *np.ndarray.flatten(self.results.gaussian_params_))

        # Create peak-removed (but not flattened) power spectrum
        self.results._spectrum_peak_rm = self.data.power_spectrum - self.results._peak_fit

        # Run final aperiodic fit on peak-removed power spectrum
        self.results.aperiodic_params_ = self._simple_ap_fit(\
            self.data.freqs, self.results._spectrum_peak_rm)
        self.results._ap_fit = self.modes.aperiodic.func(\
            self.data.freqs, *self.results.aperiodic_params_)

        # Create remaining model components: flatspec & full power_spectrum model fit
        self.results._spectrum_flat = self.data.power_spectrum - self.results._ap_fit
        self.results.modeled_spectrum_ = self.results._peak_fit + self.results._ap_fit

        ## PARAMETER UPDATES

        # Convert gaussian definitions to peak parameters
        self.results.peak_params_ = self._create_peak_params(self.results.gaussian_params_)


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


    def _get_ap_guess(self, freqs, power_spectrum):
        """Get the guess parameters for the aperiodic fit.

        Notes
        -----
        The aperiodic guess parameters currently supports pre-provided entire guess,
        or no guess at all.
        ToDo - Could be updated to fill in missing guesses.
        """

        if not self._ap_guess:

            ap_guess = []
            for label in self.modes.aperiodic.params.labels:
                if label == 'offset':
                    # Offset guess is the power value for lowest available frequency
                    ap_guess.append(power_spectrum[0])
                elif 'exponent' in label:
                    # Exponent guess is a quick calculation of the log-log slope
                    ap_guess.append(np.abs((power_spectrum[-1] - power_spectrum[0]) /
                                    (np.log10(freqs[-1]) - np.log10(freqs[0]))))
                elif 'knee' in label:
                    # Knee guess set to zero (no real guess)
                    ap_guess.append(0)
                else:
                    # Any other (un-anticipated) parameter set to guess of 0
                    ap_guess.append(0)

            ap_guess = np.array(ap_guess)

        return ap_guess


    def _set_ap_bounds(self, ap_bounds):
        """Set the default bounds for the aperiodic fit.

        Notes
        -----
        The bounds for aperiodic parameters are set in general, and currently do not update
        the constraints based on any information from the data / interim fitting results.
        """

        if ap_bounds:
            msg = 'Provided aperiodic bounds do not have right length for fit function.'
            assert len(self._ap_bounds[0]) == len(self._ap_bounds[1]) == \
                self.modes.aperiodic.n_params, msg
            self._ap_bounds = ap_bounds
        else:
            self._ap_bounds = (tuple([-np.inf] * self.modes.aperiodic.n_params),
                               tuple([np.inf] * self.modes.aperiodic.n_params))


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

        # Get the guess and bounds for the aperiodic parameters
        ap_guess = self._get_ap_guess(freqs, power_spectrum)

        # Ignore warnings that are raised in curve_fit
        #   A runtime warning can occur while exploring parameters in curve fitting
        #     This doesn't effect outcome - it won't settle on an answer that does this
        #   It happens if / when b < 0 & |b| > x**2, as it leads to log of a negative number
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                aperiodic_params, _ = curve_fit(self.modes.aperiodic.func, freqs, power_spectrum,
                                                p0=ap_guess, bounds=self._ap_bounds,
                                                maxfev=self._maxfev, check_finite=False,
                                                ftol=self._tol, xtol=self._tol, gtol=self._tol)
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
        initial_fit = self.modes.aperiodic.func(freqs, *popt)

        # Flatten power_spectrum based on initial aperiodic fit
        flatspec = power_spectrum - initial_fit

        # Flatten outliers, defined as any points that drop below 0
        flatspec[flatspec < 0] = 0

        # Use percentile threshold, in terms of # of points, to extract and re-fit
        perc_thresh = np.percentile(flatspec, self._ap_percentile_thresh)
        perc_mask = flatspec <= perc_thresh
        freqs_ignore = freqs[perc_mask]
        spectrum_ignore = power_spectrum[perc_mask]

        # Second aperiodic fit - using results of first fit as guess parameters
        #  See note in _simple_ap_fit about warnings
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                aperiodic_params, _ = curve_fit(self.modes.aperiodic.func,
                                                freqs_ignore, spectrum_ignore,
                                                p0=popt, bounds=self._ap_bounds,
                                                maxfev=self._maxfev, check_finite=False,
                                                ftol=self._tol, xtol=self._tol, gtol=self._tol)
        except RuntimeError as excp:
            error_msg = ("Model fitting failed due to not finding "
                         "parameters in the robust aperiodic fit.")
            raise FitError(error_msg) from excp
        except TypeError as excp:
            error_msg = ("Model fitting failed due to sub-sampling "
                         "in the robust aperiodic fit.")
            raise FitError(error_msg) from excp

        return aperiodic_params


    def _fit_peaks(self, flatspec):
        """Iteratively fit peaks to flattened spectrum.

        Parameters
        ----------
        flatspec : 1d array
            Flattened power spectrum values.

        Returns
        -------
        gaussian_params : 2d array
            Parameters that define the gaussian fit(s).
            Each row is a gaussian, as [mean, height, standard deviation].
        """

        # Take a copy of the flattened spectrum to iterate across
        flat_iter = np.copy(flatspec)

        # Initialize matrix of guess parameters for peak fitting
        guess = np.empty([0, self.modes.periodic.n_params])

        # Find peak: loop through, finding a candidate peak, & fit with a guess peak
        #   Stopping procedures: limit on # of peaks, or relative or absolute height thresholds
        while len(guess) < self.max_n_peaks:

            # Find candidate peak - the maximum point of the flattened spectrum
            max_ind = np.argmax(flat_iter)
            max_height = flat_iter[max_ind]

            # Stop searching for peaks once height drops below height threshold
            if max_height <= self.peak_threshold * np.std(flat_iter):
                break

            # Set the guess parameters for gaussian fitting, specifying the mean and height
            guess_freq = self.data.freqs[max_ind]
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
                fwhm = short_side * 2 * self.data.freq_res
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
            current_guess_params = (guess_freq, guess_height, guess_std)

            ## TEMP
            if self.modes.periodic.name == 'skewnorm':
                guess_skew = 0
                current_guess_params = (guess_freq, guess_height, guess_std, guess_skew)

            guess = np.vstack((guess, current_guess_params))
            peak_gauss = self.modes.periodic.func(self.data.freqs, *current_guess_params)
            flat_iter = flat_iter - peak_gauss

        # Check peaks based on edges, and on overlap, dropping any that violate requirements
        guess = self._drop_peak_cf(guess)
        guess = self._drop_peak_overlap(guess)

        # If there are peak guesses, fit the peaks, and sort results
        if len(guess) > 0:
            gaussian_params = self._fit_peak_guess(flatspec, guess)
            gaussian_params = gaussian_params[gaussian_params[:, 0].argsort()]
        else:
            gaussian_params = np.empty([0, self.modes.periodic.n_params])

        return gaussian_params


    ## TO GENERALIZE FOR MODES
    def _get_pe_bounds(self, guess):
        """Get the bound for the peak fit."""

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
        lo_bound = [bound if bound[0] > self.data.freq_range[0] else \
            [self.data.freq_range[0], *bound[1:]] for bound in lo_bound]
        hi_bound = [bound if bound[0] < self.data.freq_range[1] else \
            [self.data.freq_range[1], *bound[1:]] for bound in hi_bound]

        # Unpacks the embedded lists into flat tuples
        #   This is what the fit function requires as input
        gaus_param_bounds = (tuple(item for sublist in lo_bound for item in sublist),
                             tuple(item for sublist in hi_bound for item in sublist))

        return gaus_param_bounds


    def _fit_peak_guess(self, flatspec, guess):
        """Fits a group of peak guesses with a fit function.

        Parameters
        ----------
        flatspec : 1d array
            Flattened power spectrum values.
        guess : 2d array, shape=[n_peaks, n_params_per_peak]
            Guess parameters for periodic fits to peaks.

        Returns
        -------
        pe_params : 2d array, shape=[n_peaks, n_params_per_peak]
            Parameters for periodic fits to peaks.
        """

        # Fit the peaks
        try:
            pe_params, _ = curve_fit(self.modes.periodic.func,
                                     self.data.freqs, flatspec,
                                     p0=np.ndarray.flatten(guess),
                                     bounds=self._get_pe_bounds(guess),
                                     jac=self.modes.periodic.jacobian,
                                     maxfev=self._maxfev, check_finite=False,
                                     ftol=self._tol, xtol=self._tol, gtol=self._tol)

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
        pe_params = np.array(groupby(pe_params, self.modes.periodic.n_params))

        return pe_params


    ## TO GENERALIZE FOR MODES
    def _drop_peak_cf(self, guess):
        """Check whether to drop peaks based on center's proximity to the edge of the spectrum.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for periodic peak fits. Shape: [n_peaks, n_params_per_peak].

        Returns
        -------
        guess : 2d array
            Guess parameters for periodic peak fits. Shape: [n_peaks, n_params_per_peak].
        """

        cf_params = guess[:, 0]
        bw_params = guess[:, 2] * self._bw_std_edge

        # Check if peaks within drop threshold from the edge of the frequency range
        keep_peak = \
            (np.abs(np.subtract(cf_params, self.data.freq_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.data.freq_range[1])) > bw_params)

        # Drop peaks that fail the center frequency edge criterion
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _drop_peak_overlap(self, guess):
        """Checks whether to drop gaussians based on amount of overlap.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for periodic peak fits. Shape: [n_peaks, n_params_per_peak].

        Returns
        -------
        guess : 2d array
            Guess parameters for periodic peak fits. Shape: [n_peaks, n_params_per_peak].

        Notes
        -----
        For any peaks with an overlap >  threshold, the lowest height guess peak is dropped.
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


    ## TO GENERALIZE FOR MODES
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

        peak_params = np.empty((len(gaus_params), self.modes.periodic.n_params))

        for ii, peak in enumerate(gaus_params):

            # Gets the index of the power_spectrum at the frequency closest to the CF of the peak
            ind = np.argmin(np.abs(self.data.freqs - peak[0]))

            # Collect peak parameter data
            if self.modes.periodic.name == 'gaussian':  ## TEMP
                peak_params[ii] = [peak[0],
                                   self.results.modeled_spectrum_[ind] - self.results._ap_fit[ind],
                                   peak[2] * 2]

            ## TEMP:
            if self.modes.periodic.name == 'skewnorm':
                peak_params[ii] = [peak[0],
                                   self.results.modeled_spectrum_[ind] - self.results._ap_fit[ind],
                                   peak[2] * 2, peak[3]]

        return peak_params
