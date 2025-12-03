"""Define original spectral fitting algorithm object."""

import warnings
from itertools import repeat

import numpy as np
from numpy.linalg import LinAlgError
from scipy.optimize import curve_fit

from specparam.modutils.errors import FitError
from specparam.utils.select import groupby
from specparam.data.periodic import sort_peaks
from specparam.reports.strings import gen_width_warning_str
from specparam.measures.estimates import estimate_fwhm
from specparam.measures.params import compute_gauss_std
from specparam.algorithms.algorithm import AlgorithmCF
from specparam.algorithms.settings import SettingsDefinition

###################################################################################################
###################################################################################################

SPECTRAL_FIT_SETTINGS_DEF = SettingsDefinition({
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
            'Absolute threshold for detecting peaks.'
            '\n        '
            'This threshold is defined in absolute units of the power spectrum (log power).',
        },
    'peak_threshold' : {
        'type' : 'float, optional, default: 2.0',
        'description' : \
            'Relative threshold for detecting peaks.'
            '\n        '
            'Threshold is defined in relative units of the power spectrum (standard deviation).',
        },
})


SPECTRAL_FIT_PRIVATE_SETTINGS_DEF = SettingsDefinition({
    'ap_percentile_thresh' : {
        'type' : 'float',
        'description' : \
            'Percentile threshold to select data from flat spectrum for an initial aperiodic fit.'
            '\n        '
            'Points are selected at a low percentile value to restrict to non-peak points.',
        },
    'ap_guess' : {
        'type' : 'list of float',
        'description' : \
            'Guess parameters for fitting the aperiodic component.'
            '\n        '
            'The guess parameters should match the length and order of the aperiodic parameters.'
            '\n        '
            'If \'offset\' is a parameter, default guess is the first value of the power spectrum.'
            '\n        '
            'If \'exponent\' is a parameter, '
            'default guess is the abs(log-log slope) of first & last points.'
        },
    'ap_bounds' : {
        'type' : 'tuple of tuple of float',
        'description' : \
            'Bounds for aperiodic fitting, as ((param1_low_bound, ...) (param1_high_bound, ...)).'
            '\n        '
            'By default, aperiodic fitting is unbound, but can be restricted here.',
        },
    'cf_bound' : {
        'type' : 'float',
        'description' : \
            'Parameter bounds for center frequency when fitting peaks, as +/- std dev.',
        },
    'bw_std_edge' : {
        'type' : 'float',
        'description' : \
            'Threshold for how far a peak has to be from edge to keep.'
            '\n        '
            'This is defined in units of peak standard deviation.',
        },
    'gauss_overlap_thresh' : {
        'type' : 'float',
        'description' : \
            'Degree of overlap between peak guesses for one to be dropped.'
            '\n        '
            'This is defined in units of peak standard deviation.',
        },
})


class SpectralFitAlgorithm(AlgorithmCF):
    """Base object defining model & algorithm for spectral parameterization.

    Parameters
    ----------
    % public settings described in Spectral Fit Algorithm Settings
    """
    # pylint: disable=attribute-defined-outside-init

    def __init__(self, peak_width_limits=(0.5, 12.0), max_n_peaks=np.inf, min_peak_height=0.0,
                 peak_threshold=2.0, ap_percentile_thresh=0.025, ap_guess=None, ap_bounds=None,
                 cf_bound=1.5, bw_std_edge=1.0, gauss_overlap_thresh=0.75, maxfev=5000,
                 tol=0.00001, modes=None, data=None, results=None, debug=False):
        """Initialize base model object"""

        # Initialize base algorithm object with algorithm metadata
        super().__init__(
            name='spectral_fit',
            description='Original parameterizing neural power spectra algorithm.',
            public_settings=SPECTRAL_FIT_SETTINGS_DEF,
            private_settings=SPECTRAL_FIT_PRIVATE_SETTINGS_DEF,
            modes=modes, data=data, results=results, debug=debug)

        ## Public settings
        self.settings.peak_width_limits = peak_width_limits
        self.settings.max_n_peaks = max_n_peaks
        self.settings.min_peak_height = min_peak_height
        self.settings.peak_threshold = peak_threshold

        ## Private settings: model parameters related settings
        self._settings.ap_percentile_thresh = ap_percentile_thresh
        self._settings.ap_guess = ap_guess
        self._settings.ap_bounds = self._get_ap_bounds(ap_bounds)
        self._settings.cf_bound = cf_bound
        self._settings.bw_std_edge = bw_std_edge
        self._settings.gauss_overlap_thresh = gauss_overlap_thresh

        ## curve_fit settings
        # Note - default reduces tolerance to speed fitting (as compared to curve_fit's default).
        #   Set value to 1e-8 to match curve_fit default.
        self._cf_settings.maxfev = maxfev
        self._cf_settings.tol = tol


    def _fit_prechecks(self, verbose=True):
        """Prechecks to run before the fit function.

        Notes
        -----
        Checks peak width limits and raises a warning if lower limit is too
        low given the frequency resolution of the data.
        """

        if verbose:
            if 1.5 * self.data.freq_res >= self.settings.peak_width_limits[0]:
                print(gen_width_warning_str(self.data.freq_res,
                                            self.settings.peak_width_limits[0]))


    def _fit(self):
        """Define the full fitting algorithm."""

        ## FIT PROCEDURES

        # Take an initial fit of the aperiodic component
        temp_aperiodic_params = self._robust_ap_fit(self.data.freqs, self.data.power_spectrum)
        temp_ap_fit = self.modes.aperiodic.func(self.data.freqs, *temp_aperiodic_params)

        # Find peaks from the flattened power spectrum, and fit them
        temp_spectrum_flat = self.data.power_spectrum - temp_ap_fit
        self.results.params.periodic.add_params('fit', self._fit_peaks(temp_spectrum_flat))

        # Calculate the peak fit
        #   Note: if no peaks are found, this creates a flat (all zero) peak fit
        self.results.model._peak_fit = self.modes.periodic.func(\
            self.data.freqs, *np.ndarray.flatten(self.results.params.periodic.get_params('fit')))

        # Create peak-removed (but not flattened) power spectrum
        self.results.model._spectrum_peak_rm = \
            self.data.power_spectrum - self.results.model._peak_fit

        # Run final aperiodic fit on peak-removed power spectrum
        self.results.params.aperiodic.add_params('fit', \
            self._simple_ap_fit(self.data.freqs, self.results.model._spectrum_peak_rm))
        self.results.model._ap_fit = self.modes.aperiodic.func(\
            self.data.freqs, *self.results.params.aperiodic.params)

        # Create remaining model components: flatspec & full power_spectrum model fit
        self.results.model._spectrum_flat = self.data.power_spectrum - self.results.model._ap_fit
        self.results.model.modeled_spectrum = \
            self.results.model._peak_fit + self.results.model._ap_fit


    def _get_ap_guess(self, freqs, power_spectrum):
        """Get the guess parameters for the aperiodic fit.

        Notes
        -----
        The aperiodic guess parameters currently supports pre-provided entire guess,
        or no guess at all.
        ToDo - Could be updated to fill in missing guesses.
        """

        if not self._settings.ap_guess:

            ap_guess = self._initialize_guess('aperiodic')

            for label, ind in self.modes.aperiodic.params.indices.items():
                if label == 'offset':
                    # Offset guess is the power value for lowest available frequency
                    ap_guess[ind] = power_spectrum[0]
                elif 'exponent' in label:
                    # Exponent guess is a quick calculation of the log-log slope
                    ap_guess[ind] = np.abs((power_spectrum[-1] - power_spectrum[0]) /
                                           (np.log10(freqs[-1]) - np.log10(freqs[0])))

        return ap_guess


    def _get_ap_bounds(self, ap_bounds):
        """Set the default bounds for the aperiodic fit.

        Parameters
        ----------
        bounds : tuple of tuple or None
            Bounds definition. If None, creates default bounds.

        Returns
        -------
        bounds : tuple of tuple
            Bounds definition.

        Notes
        -----
        The bounds for aperiodic parameters are set in general, and currently do not update
        the constraints based on any information from the data / interim fitting results.
        """

        if ap_bounds:
            msg = 'Provided aperiodic bounds do not have right length for fit function.'
            assert len(ap_bounds[0]) == len(ap_bounds[1]) == self.modes.aperiodic.n_params, msg
        else:
            ap_bounds = self._initialize_bounds('aperiodic')

        return ap_bounds


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
                                                p0=ap_guess, bounds=self._settings.ap_bounds,
                                                maxfev=self._cf_settings.maxfev,
                                                check_finite=False,
                                                ftol=self._cf_settings.tol,
                                                xtol=self._cf_settings.tol,
                                                gtol=self._cf_settings.tol)
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
        perc_thresh = np.percentile(flatspec, self._settings.ap_percentile_thresh)
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
                                                p0=popt, bounds=self._settings.ap_bounds,
                                                maxfev=self._cf_settings.maxfev,
                                                check_finite=False,
                                                ftol=self._cf_settings.tol,
                                                xtol=self._cf_settings.tol,
                                                gtol=self._cf_settings.tol)
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
        peak_params : 2d array
            Parameters that define the peak fit(s).
        """

        # Take a copy of the flattened spectrum to iterate across
        flat_iter = np.copy(flatspec)

        # Initialize matrix of guess parameters for peak fitting
        guess = np.empty([0, self.modes.periodic.n_params])

        # Find peak: loop through, finding a candidate peak, & fit with a guess peak
        #   Stopping procedures: limit on # of peaks, or relative or absolute height thresholds
        while len(guess) < self.settings.max_n_peaks:

            # Find candidate peak - the maximum point of the flattened spectrum
            max_ind = np.argmax(flat_iter)
            max_height = flat_iter[max_ind]

            # Stop searching for peaks once height drops below height threshold
            if max_height <= self.settings.peak_threshold * np.std(flat_iter):
                break

            # Set the guess parameters for peak fitting, specifying the mean and height
            guess_freq = self.data.freqs[max_ind]
            guess_height = max_height

            # Halt fitting process if candidate peak drops below minimum height
            if not guess_height > self.settings.min_peak_height:
                break

            # Estimate FWHM, and use to convert to an estimated Gaussian std
            #   If estimation process fails, then default guess to average of limits
            fwhm = estimate_fwhm(flat_iter, max_ind, self.data.freq_res)
            guess_std = compute_gauss_std(fwhm) if not np.isnan(fwhm) else \
                np.mean(self.settings.peak_width_limits)

            # Check that guess value isn't outside preset limits - restrict if so
            #   This also converts the peak_width_limits from 2-sided BW to 1-sided std
            #   Note: without this, curve_fitting fails if given guess > or < bounds
            if guess_std < self.settings.peak_width_limits[0] / 2:
                guess_std = self.settings.peak_width_limits[0] / 2
            if guess_std > self.settings.peak_width_limits[1] / 2:
                guess_std = self.settings.peak_width_limits[0] / 2

            # Collect guess parameters
            cur_guess = [0] * self.modes.periodic.n_params
            cur_guess[self.modes.periodic.params.indices['cf']] = guess_freq
            cur_guess[self.modes.periodic.params.indices['pw']] = guess_height
            cur_guess[self.modes.periodic.params.indices['bw']] = guess_std

            # Fit and subtract guess peak from the spectrum
            guess = np.vstack((guess, cur_guess))
            peak_fit = self.modes.periodic.func(self.data.freqs, *cur_guess)
            flat_iter = flat_iter - peak_fit

        # Check peaks based on edges, and on overlap, dropping any that violate requirements
        guess = self._drop_peak_cf(guess)
        guess = self._drop_peak_overlap(guess)

        # If there are peak guesses, fit the peaks, and sort results by CF
        if len(guess) > 0:
            peak_params = self._fit_peak_guess(flatspec, guess)
            peak_params = sort_peaks(peak_params, 'CF', 'inc')

        else:
            peak_params = np.empty([0, self.modes.periodic.n_params])

        return peak_params


    def _get_pe_bounds(self, guess):
        """Get the bound for the peak fit.

        Parameters
        ----------
        guess : list
            Guess parameters from initial peak search.

        Returns
        -------
        pe_bounds : tuple of array
            Bounds for periodic fit.
        """

        n_pe_params = self.modes.periodic.n_params
        bounds = repeat(self._initialize_bounds('periodic'))
        bounds_lo = np.empty(len(guess) * n_pe_params)
        bounds_hi = np.empty(len(guess) * n_pe_params)

        for p_ind, peak in enumerate(guess):
            for label, ind in self.modes.periodic.params.indices.items():

                pbounds_lo, pbounds_hi = next(bounds)

                if label == 'cf':
                    # Set boundaries on CF, weighted by the bandwidth
                    peak_bw = peak[self.modes.periodic.params.indices['bw']]
                    lcf = peak[ind] - 2 * self._settings.cf_bound * peak_bw
                    hcf = peak[ind] + 2 * self._settings.cf_bound * peak_bw
                    # Check that CF bounds are within frequency range - if not restrict to range
                    pbounds_lo[ind] = lcf if lcf > self.data.freq_range[0] \
                        else self.data.freq_range[0]
                    pbounds_hi[ind] = hcf if hcf < self.data.freq_range[1] \
                        else self.data.freq_range[1]

                if label == 'pw':
                    # Enforce positive values for height
                    pbounds_lo[ind] = 0

                if label == 'bw':
                    # Set bandwidth limits, converting limits from Hz to guess params in std
                    pbounds_lo[ind] = self.settings.peak_width_limits[0] / 2
                    pbounds_hi[ind] = self.settings.peak_width_limits[1] / 2

            bounds_lo[p_ind*n_pe_params:(p_ind+1)*n_pe_params] = pbounds_lo
            bounds_hi[p_ind*n_pe_params:(p_ind+1)*n_pe_params] = pbounds_hi

        pe_bounds = (bounds_lo, bounds_hi)

        return pe_bounds


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
                                     maxfev=self._cf_settings.maxfev,
                                     check_finite=False,
                                     ftol=self._cf_settings.tol,
                                     xtol=self._cf_settings.tol,
                                     gtol=self._cf_settings.tol)

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

        cf_params = guess[:, self.modes.periodic.params.indices['cf']]
        bw_params = guess[:, self.modes.periodic.params.indices['bw']] * self._settings.bw_std_edge

        # Check if peaks within drop threshold from the edge of the frequency range
        keep_peak = \
            (np.abs(np.subtract(cf_params, self.data.freq_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.data.freq_range[1])) > bw_params)

        # Drop peaks that fail the center frequency edge criterion
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess


    def _drop_peak_overlap(self, guess):
        """Checks whether to drop peaks based on amount of overlap.

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

        inds = self.modes.periodic.params.indices

        # Sort the peak guesses by increasing frequency
        #   This is so adjacent peaks can be compared from right to left
        guess = sorted(guess, key=lambda x: float(x[inds['cf']]))

        # Calculate standard deviation bounds for checking amount of overlap
        #   The bounds are the center frequency +/- width (standard deviation)
        bounds = [[peak[inds['cf']] - peak[inds['bw']] * self._settings.gauss_overlap_thresh,
                   peak[inds['cf']] + peak[inds['bw']] * self._settings.gauss_overlap_thresh]\
                   for peak in guess]

        # Loop through peak bounds, comparing current bound to that of next peak
        #   If the left peak's upper bound extends pass the right peaks lower bound,
        #   then drop the Gaussian with the lower height
        drop_inds = []
        for ind, b_0 in enumerate(bounds[:-1]):
            b_1 = bounds[ind + 1]

            # Check if bound of current peak extends into next peak
            if b_0[1] > b_1[0]:

                # If so, get the index of the peak with the lowest height (to drop)
                drop_inds.append([ind, ind + 1][np.argmin([guess[ind][1], guess[ind + 1][1]])])

        # Drop any peaks guesses that overlap too much, based on threshold
        keep_peak = [not ind in drop_inds for ind in range(len(guess))]
        guess = np.array([gu for (gu, keep) in zip(guess, keep_peak) if keep])

        return guess
