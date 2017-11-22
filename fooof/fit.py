"""FOOOF - Fitting Oscillations & One-Over F"""

import os
import warnings
from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.optimize import curve_fit

from fooof.utils import group_three, trim_psd
from fooof.funcs import gaussian_function, loglorentzian_function, loglorentzian_nk_function

###################################################################################################
###################################################################################################

FOOOFResult = namedtuple('FOOOFResult', ['background_params', 'oscillations_params', 'r2', 'error'])

class FOOOF(object):
    """Model the physiological power spectrum as oscillatory peaks and 1/f background.

    NOTE: FOOOF expects frequency and power values in linear space.
        Passing in logged frequencies and/or power spectra is not detected,
            and will silently produce incorrect results.

    Parameters
    ----------
    bandwidth_limits : tuple of (float, float), optional (default: (0.5, 12.0)
        Setting to exclude gaussian fits where the bandwidth is implausibly narrow or wide.
    max_n_oscs : int, optional (default: inf)
        Maximum number of oscillations to be modeled in a single PSD.
    min_amp : float, optional (default: 0)
        Minimum amplitude threshold for an oscillation to be modeled.
    amp_std_thresh : float, optional (default: 2.0)
        Amplitude threshold for detecting oscillatory peaks, units of standard deviation.
    fit_knee : boolean, optional (default: False)
        Whether to fit a knee parameter in the lorentzian background fit.
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
    oscillation_params_ : 1d array
        Fitted parameter values for the oscillations.
    r2_ : float
        R-squared between the input PSD and the full model fit.
    error_ : float
        R-squared error of the full model fit.
    _psd_flat : 1d array
        Flattened PSD (background 1/f removed)
    _psd_osc_rm : 1d array
        PSD with oscillations removed (not flattened).
    _gaussian_params : 2d array
        Parameters that define the gaussian fit(s). Each row is an oscillation, as [CF, amp, BW].
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

    Notes
    -----
    - Input PSD should be smooth - overly noisy power spectra may lead to bad fits.
        - In particular, raw FFT inputs are not appropriate, we recommend using either Welch's
        procedure, or a median filter smoothing on the FFT output before running FOOOF.
        - Where possible and appropriate, use longer time segments for PSD calculation to
        get smoother PSDs; this will give better FOOOF fits.
    """

    def __init__(self, bandwidth_limits=(0.5, 12.0), max_n_oscs=np.inf,
                 min_amp=0.0, amp_std_thresh=2.0, fit_knee=False, verbose=True):
        """Initialize FOOOF object with run parameters."""

        # Set lorentzian function version for whether fitting knee or not
        self.fit_knee = fit_knee
        global lorentzian_function
        lorentzian_function = loglorentzian_function if self.fit_knee else loglorentzian_nk_function

        # Set input parameters
        self.bandwidth_limits = bandwidth_limits
        self.max_n_oscs = max_n_oscs
        self.min_amp = min_amp
        self.amp_std_thresh = amp_std_thresh
        self.verbose = verbose

        ## SETTINGS
        # Noise threshold, as a percentage of the lowest amplitude values in the total data to fit.
        #  Defines the minimum amplitude, above residuals, to be considered an oscillation.
        self._bg_amp_thresh = 0.025
        # Guess parameters for background fitting, [offset, knee, slope]
        #  If offset guess is None, the first value of the PSD is used as offset guess
        self._bg_guess = [None, 0, 2]
        # Bounds for background fitting, as: ((offset_low_bound, knee_low_bound, sl_low_bound),
        #                                (offset_high_bound, knee_high_bound, sl_high_bound))
        #  By default, background fitting is unbound, but can be restricted here, if desired
        #    Even if fitting without knee, leave bounds for knee (they are dropped later)
        self._bg_bounds = ((-np.inf, -np.inf, -np.inf), (np.inf, np.inf, np.inf))
        # Threshold for how far (units of gaus std dev) an oscillation has to be from edge to keep.
        self._bw_std_edge = 1.0
        # Parameter bounds for center frequency when fitting gaussians - in terms of +/- std dev
        self._cf_bound = 1.5

        # INTERAL PARAMETERS
        # Bandwidth limits are given in 2-sided oscillation bandwidth.
        #  Convert to gaussian std parameter limits.
        self._std_limits = [bwl / 2 for bwl in self.bandwidth_limits]
        # Bounds for background fitting. Drops bounds on knee parameter if not set to fit knee
        self._bg_bounds = self._bg_bounds if self.fit_knee else tuple(b[0::2] for b in self._bg_bounds)

        # Initialize all data attributes (to None)
        self._reset_dat()


    def _reset_dat(self):
        """Set (or reset) all data attributes to empty."""

        self.freqs = None
        self.psd = None
        self.freq_range = None
        self.freq_res = None
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


    def model(self, freqs, psd, freq_range, plt_log=False):
        """Run model fit, plot, and print results.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.
        freq_range : list of [float, float]
            Desired frequency range to run FOOOF on.
        """

        self.fit(freqs, psd, freq_range)
        self.plot(plt_log)
        self.print_results()


    def fit(self, freqs, psd, freq_range):
        """Fit the full PSD as 1/f and gaussian oscillations.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD, linear.
        psd : 1d array
            Power spectral density values, linear.
        freq_range : list of [float, float]
            Desired frequency range to run FOOOF on.
        """

        # Clear any potentially old data (that could interfere).
        self._reset_dat()

        # Check inputs dimensions & size
        if freqs.ndim != freqs.ndim != 1:
            raise ValueError('Inputs are not 1 dimensional.')
        if freqs.shape != psd.shape:
            raise ValueError('Inputs are not consistent size.')

        # Calculate and store frequency resolution.
        self.freq_res = freqs[1] - freqs[0]

        # Log frequency inputs
        psd = np.log10(psd)

        # Trim the PSD to requested frequency range.
        self.freq_range = freq_range
        self.freqs, self.psd = trim_psd(freqs, psd, self.freq_range)

        # Check bandwidth limits against frequency resolution; warn if too close.
        if round(self.freq_res, 1) >= self.bandwidth_limits[0] and self.verbose:
            print('\nFOOOF WARNING: Lower-bound Bandwidth limit is ~= the frequency resolution. \n',
                  '  This may lead to overfitting of small bandwidth oscillations.\n')

        # Fit the background 1/f.
        self._background_fit, self.background_params_ = self._clean_background_fit(
            self.freqs, self.psd)

        # Flatten the PSD using fit background.
        self._psd_flat = self.psd - self._background_fit

        # Find oscillations, and fit them with gaussians.
        self._gaussian_params = self._fit_oscs(np.copy(self._psd_flat))

        # Calculate the oscillation fit.
        #  Note: if no oscillations are found, this creates a flat (all zero) oscillation fit.
        self._oscillation_fit = gaussian_function(
            self.freqs, *np.ndarray.flatten(self._gaussian_params))

        # Create oscillation-removed (but not flattened) PSD.
        self._psd_osc_rm = self.psd - self._oscillation_fit

        # Run final background fit on oscillation-removed PSD.
        #   Note: This overwrites previous background fit.
        self._background_fit, self.background_params_ = self._quick_background_fit(
            self.freqs, self._psd_osc_rm)

        # Create full PSD model fit.
        self.psd_fit_ = self._oscillation_fit + self._background_fit

        # Copy the gaussian params to oscillations outputs, updating as appropriate.
        #  Amplitude is updated to the amplitude of oscillation above the background fit.
        #   This is returned instead of the gaussian amplitude
        #    Actual amplitude is harder to interpret, due to osc overlaps.
        #  Bandwidth is updated to be 'both-sided'
        #   This is as opposed to gaussian std param, which is 1-sided.
        self.oscillation_params_ = np.empty([0, 3])
        for i, osc in enumerate(self._gaussian_params):
            # Gets the index of the PSD at the frequency closest to the CF of the osc
            ind = min(range(len(self.freqs)), key=lambda i: abs(self.freqs[i] - osc[0]))
            # Collect oscillation parameter data
            self.oscillation_params_ = np.vstack((self.oscillation_params_,
                                                 [osc[0],
                                                  self.psd_fit_[ind] - self._background_fit[ind],
                                                  osc[2] * 2]))

        # Calculate R^2 and error of the model fit.
        self._r_squared()
        self._rmse_error()


    def plot(self, plt_log=False, save_fig=False, save_path='', save_name='FOOOF_fit.png', ax=None):
        """Plot the original PSD, and full model fit.

        Parameters
        ----------
        plt_log : boolean, optional
            Whether or not to plot the frequency axis in log space. default: False
        save_fig : boolean, optional
            Whether to save out a copy of the plot. default : False
        save_path :
            xx
        save_name : str, optional
            xx
        ax : ?
            xx
        """

        # Throw an error if FOOOF model hasn't been fit yet
        if not np.all(self.freqs):
            raise ValueError('Model fit has not been run - can not proceed.')

        # Set frequency vector, logged if requested
        plt_freqs = np.log10(self.freqs) if plt_log else self.freqs

        # Create plot axes, if not provided
        if not ax:
            fig, ax = plt.subplots(figsize=(12, 10))

        # Create the plot
        ax.plot(plt_freqs, self.psd, 'k', linewidth=1.0)
        ax.plot(plt_freqs, self.psd_fit_, 'r', linewidth=3.0, alpha=0.5)
        ax.plot(plt_freqs, self._background_fit, '--b', linewidth=3.0, alpha=0.5)

        ax.set_xlabel('Frequency', fontsize=20)
        ax.set_ylabel('Power', fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=16)

        ax.legend(['Original PSD', 'Full model fit', 'Background fit'], prop={'size': 16})
        ax.grid()

        # Save out figure, if requested
        if save_fig:
            plt.savefig(os.path.join(save_path, save_name))


    def get_results(self):
        """Return model fit parameters and error."""

        return FOOOFResult(self.background_params_, self.oscillation_params_, self.r2_, self.error_)


    def print_results(self):
        """Print out the PSD model fit results."""

        print(self._gen_results_str())


    def print_settings(self, description=False):
        """Print out the current FOOOF settings.

        Parameters
        ----------
        description : bool, optional (default: True)
            Whether to print out a description with current settings.

        Notes
        -----
        - This only prints out user defined settings, accessible at initialization.
        - There are also internal settings, documented and defined in __init__
        """

        print(self._gen_settings_str(description))


    def create_report(self):
        """Generate and save out a report of the current FOOOF fit."""

        # Set the font description for saving out text with matplotlib
        font = {'family': 'monospace',
                'weight': 'normal',
                'size': 16}

        # Set up outline figure, using gridspec
        fig = plt.figure(figsize=(16, 20))
        gs = gridspec.GridSpec(3, 1, height_ratios=[0.8, 1.0, 0.7])

        # First - text results
        ax0 = plt.subplot(gs[0])
        results_str = self._gen_results_str()
        ax0.text(0.5, 0.2, results_str, font, ha='center');
        ax0.set_frame_on(False)
        ax0.set_xticks([])
        ax0.set_yticks([])

        # Second - data plot
        ax1 = plt.subplot(gs[1])
        self.plot(ax=ax1)

        # Third - FOOOF settings
        ax2 = plt.subplot(gs[2])
        settings_str = self._gen_settings_str(False)
        ax2.text(0.5, 0.2, settings_str, font, ha='center')
        ax2.set_frame_on(False)
        ax2.set_xticks([])
        ax2.set_yticks([])

        # Save out the report
        plt.savefig('whole_fig.pdf')
        plt.close()


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
        psd_fit_ : 1d array
            Values of fit background.
        popt : list of [offset, knee, slope]
            Parameter estimates.
        """

        # Set guess params for lorentzian background fit, guess params set at init
        guess = np.array(([psd[0]] if not self._bg_guess[0] else [self._bg_guess[0]]) +
                         ([self._bg_guess[1]] if self.fit_knee else []) +
                         [self._bg_guess[2]])

        # Ignore warnings that are raised in curve_fit
        #  A runtime warning can occur while exploring parameters in curve fitting
        #    This doesn't effect outcome - it won't settle on an answer that does this
        #  It happens if / when b < 0 & |b| > x**2, as it leads to log of a negative number
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            popt, _ = curve_fit(lorentzian_function, freqs, psd, p0=guess,
                                maxfev=5000, bounds=self._bg_bounds)

        # Calculate the actual background fit
        psd_fit_ = lorentzian_function(freqs, *popt)

        return psd_fit_, popt


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
        background_fit : 1d array
            background PSD.
        background_params_ : 1d array
            Parameters of background fit (length of 3: offset, knee, slope).
        """

        # Do a quick, initial background fit.
        initial_fit, popt = self._quick_background_fit(freqs, psd)

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
            background_params_, _ = curve_fit(lorentzian_function, f_ignore, psd_ignore,
                                              p0=popt, maxfev=5000, bounds=self._bg_bounds)

        # Calculate the actual background fit.
        background_fit = lorentzian_function(freqs, *background_params_)

        return background_fit, background_params_


    def _fit_oscs(self, flat_iter):
        """Iteratively fit oscillations to flattened spectrum.

        Parameters
        ----------
        flat_iter : 1d array
            Flattened PSD values.

        Returns
        -------
        gaussian_params : 2d array
            Parameters for gaussian fits to oscillations. Shape = [n_oscs, 3], row: [CF, AMP, STD].
        """

        # Initialize matrix of guess parameters for gaussian fitting.
        guess = np.empty([0, 3])

        # Find oscillations: Loop through, checking residuals, stopping based on std check
        while len(guess) < self.max_n_oscs:

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

            # Estimate std properly from FWHM.
            #  Calculate FWHM, converting to Hz.
            fwhm = shortest_side * 2 * self.freq_res
            #  Calulate guess gaussian std from FWHM.
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
        for i, b0 in enumerate(bounds[:-1]):
            b1 = bounds[i + 1]

            # Check if bound of current oscillations extends into next oscillation
            if b0[1] > b1[0]:

                # If so, get the index of the lowest amplitude oscillation (to drop)
                drop_inds.append([i, i + 1][np.argmin([guess[i][1], guess[i + 1][1]])])

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


    def _gen_settings_str(self, description=False):
        """Generate a string representation of current FOOOF settings.

        Parameters
        ----------
        description : bool, optional (default: True)
            Whether to print out a description with current settings.
        """

        # Center value for spacing
        cen_val = 100

        # Parameter descriptions to print out
        desc = {'fit_knee'  : 'Whether to fit a knee parameter in background fitting.',
                'bw_lims'    : 'The possible range of bandwidths for extracted oscillations, in Hz.',
                'num_oscs'   : 'The maximum number of oscillations that can be extracted.',
                'min_amp'    : 'Minimum absolute amplitude, above background, for an oscillation to be extracted.',
                'amp_thresh' : 'Threshold, in units of standard deviation, at which to stop searching for oscillations.'}

        # Clear description for printing if not requested
        if not description:
            desc = {k : '' for k, v in desc.items()}

        # Create output string
        output = '\n'.join([

            # Header
            '=' * cen_val,
            '',
            'FOOOF - SETTINGS'.center(cen_val),
            '',

            # Settings - include descriptions if requested
            *[el for el in ['Fit Knee : {}'.format(self.fit_knee).center(cen_val),
            '{}'.format(desc['fit_knee']).center(cen_val),
            'Bandwidth Limits : {}'.format(self.bandwidth_limits).center(cen_val),
            '{}'.format(desc['bw_lims']).center(cen_val),
            'Max Number of Oscillations : {}'.format(self.max_n_oscs).center(cen_val),
            '{}'.format(desc['num_oscs']).center(cen_val),
            'Minimum Amplitude : {}'.format(self.min_amp).center(cen_val),
            '{}'.format(desc['min_amp']).center(cen_val),
            'Amplitude Threshold: {}'.format(self.amp_std_thresh).center(cen_val),
            '{}'.format(desc['amp_thresh']).center(cen_val)] if not el == ' '*cen_val],

            # Footer
            '',
            '=' * cen_val
        ])

        return output


    def _gen_results_str(self):
        """Generate a string representation of model fit results."""

        if not np.all(self.freqs):
            raise ValueError('Model fit has not been run - can not proceed.')

        # Set centering value.
        cen_val = 100

        # Create output string
        output = '\n'.join([

            # Header
            '=' * cen_val,
            '',
            ' FOOOF - PSD MODEL'.center(cen_val),
            '',

            # Frequency range and resolution
            'The input PSD was modelled in the frequency range: {} - {} Hz'.format(
                self.freq_range[0], self.freq_range[1]).center(cen_val),
            'Frequency Resolution is {:1.2f} Hz'.format(self.freq_res).center(cen_val),
            '',

            # Background parameters
            ('Background Parameters (offset, ' + ('knee, ' if self.fit_knee else '') + \
               'slope): ').center(cen_val),
            ', '.join(['{:2.4f}'] * len(self.background_params_)).format(
                *self.background_params_).center(cen_val),
            '',

            # Oscillation parameters
            '{} oscillations were found:'.format(
                len(self.oscillation_params_)).center(cen_val),
            *['CF: {:6.2f}, Amp: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]).center(cen_val) \
              for op in self.oscillation_params_],
            '',

            # R^2 and error
            'R^2 of model fit is {:5.4f}'.format(self.r2_).center(cen_val),
            'Root mean squared error of model fit is {:5.4f}'.format(
                self.error_).center(cen_val),
            '',

            # Footer
            '=' * cen_val
        ])

        return output
