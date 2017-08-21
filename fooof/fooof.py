"""FOOOF!

DEPENDENCIES: SCIPY >0.19
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from fooof.utils import group_three, trim_psd
from fooof.funcs import gaussian_function, linear_function, quadratic_function

###################################################################################################
###################################################################################################
###################################################################################################

class FOOOF(object):
    """Model the physiological power spectrum as oscillatory peaks and 1/f background.

    WARNING: INPUT IS LOGGED PSD & LINEAR FREQS (TO FIX, THEN UPDATE WARNING)

    Parameters
    ----------
    bandwidth_limits : list of [float, float]
        Setting to exclude gaussian fits where the bandwidth is implausibly narrow or wide

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
    psd_fit : 1d array
        The full model fit of the PSD - 1/f & oscillations across freq_range.
    background_params : 1d array
        Parameters that define the background fit.
    oscillation_params : 1d array
        Fit values for the oscillations.
    error : float
        R-squared error of the full model fit.
    _psd_flat : 1d array
        Flattened PSD.
    _psd_osc_rm : 1d array
        PSD with oscillations removed (not flattened).
    _gaussian_params : 2d array
        Parameters that define the gaussian fit(s). Each row is an oscillation, as [CF, Amp, BW].
    _background_fit : 1d array
        Values of the background fit.
    _oscillation_fit : 1d array
        Values of the oscillation fit (flattened).
    _sl_amp_thresh : float
        Noise threshold for slope fitting.
    _sl_param_bounds :
        Parameter bounds for background fitting.
    _amp_std_thresh : float
        Amplitude threshold for detecting oscillatory peaks, units of standard deviation.
    _bw_std_thresh : float
        Banwidth threshold for edge rejection of oscillations, units of standard deviation.

    Notes
    -----
    - Input PSD should be smooth. We recommend ... TODO
    """

    def __init__(self, bandwidth_limits=[0.5, 8]):
        """Initialize FOOOF object with run parameters."""

        # Set input parameters
        self.bandwidth_limits = bandwidth_limits

        ## SETTINGS
        # Noise threshold, as a percentage of the data.
        #  This threshold defines the minimum amplitude, above residuals, to be considered an oscillation
        self._sl_amp_thresh = 0.025
        # Default 1/f parameter bounds. This limits slope to be less than 2 and no steeper than -8.
        self._sl_param_bounds = (-np.inf, -8, 0), (np.inf, 2, np.inf)
        # St. deviation threshold, above residuals, to consider a peak an oscillation
        #   TODO: SEE NOTE IN FIT_OSCS about this parameter
        self._amp_std_thresh = 2.0
        # Threshold for how far (in units of standard deviation) an oscillation has to be from edge to keep
        self._bw_std_thresh = 1.

        # Initialize all data attributes (to None)
        self._reset_dat()


    def _reset_dat(self):
        """Set (or reset) all data attributes to empty"""

        self.freqs = None
        self.psd = None
        self.freq_range = None
        self.freq_res = None
        self.psd_fit = None
        self.background_params = None
        self.oscillation_params = None
        self.error = None

        self._psd_flat = None
        self._psd_osc_rm = None
        self._gaussian_params = None
        self._background_fit = None
        self._oscillation_fit = None


    def model(self, freqs, psd, freq_range):
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
        self.plot()
        self.print_params()


    def fit(self, freqs, psd, freq_range):
        """Fit the full PSD as 1/f and gaussian oscillations.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.
        freq_range : list of [float, float]
            Desired frequency range to run FOOOF on.
        """

        # Clear any potentially old data (that could interfere)
        self._reset_dat()

        # Check inputs dimensions & size
        if freqs.ndim != freqs.ndim != 1:
            raise ValueError('Inputs are not 1 dimensional.')
        if freqs.shape != psd.shape:
            raise ValueError('Inputs are not consistent size.')

        # Calculate and store frequency resolution
        self.freq_res = freqs[1] - freqs[0]

        # Trim the PSD to requested frequency range
        self.freq_range = freq_range
        self.freqs, self.psd = trim_psd(freqs, psd, self.freq_range)

        # Fit the background 1/f
        self._background_fit, self.background_params = self._clean_background_fit(self.freqs, self.psd)

        # Flatten the PSD using fit background
        psd_flat = self.psd - self._background_fit
        # NOTE: Still drop below zero points?
        psd_flat[psd_flat < 0] = 0
        self._psd_flat = psd_flat

        # Fit initial oscillation gaussian fit
        self._gaussian_params = self._fit_oscs(np.copy(self._psd_flat))

        # Calculate the oscillation fit
        #  Note: if no oscillations are found, this creates a flat (all zero) oscillation fit
        self._oscillation_fit = gaussian_function(self.freqs, *np.ndarray.flatten(self._gaussian_params))

        # Create oscillation removed (but not flat) PSD
        self._psd_osc_rm = self.psd - self._oscillation_fit

        # Run final slope fit on oscillation removed psd
        #   Note: This overwrites previous slope fit
        #       Q: is it an issue final slope fit not the one used during oscillation fitting?
        self._background_fit, self.background_params = self._quick_background_fit(np.log10(self.freqs),
                                                                                  self._psd_osc_rm)

        # Create full PSD model fit
        self.psd_fit = self._oscillation_fit + self._background_fit

        # Copy the gaussian params to oscillations outputs, updating amplitude value
        #  Amplitude is update to the amplitude of oscillation above the background fit
        #  This is returned instead of the gaussian amplitude, which is harder to interpret, due to osc overlaps
        # NOTE: Currently, calculates based on nearest actual point. Should we instead estimate based an actual CF?
        self.oscillation_params = np.empty([0, 3])
        for i, osc in enumerate(self._gaussian_params):
            ind = min(range(len(self.freqs)), key=lambda i: abs(self.freqs[i]-osc[0]))
            self.oscillation_params = np.vstack((self.oscillation_params, [osc[0],
                                                 self.psd_fit[ind] - self._background_fit[ind], osc[2] * 2]))

        # Calculate error of the model fit
        self._r_squared()


    def plot(self):
        """Plot the original PSD, and full model fit.
        NOTE: Should we plot in semi-log, or log-log?
        """

        plt.figure(figsize=(14, 10))

        plt.plot(self.freqs, self.psd, 'k')
        plt.plot(self.freqs, self.psd_fit, 'b')
        plt.plot(self.freqs, self._background_fit, '--g')

        plt.legend(['Original PSD', 'Full model fit', 'Background fit'], prop={'size': 18})


    def print_params(self):
        """Print out the PSD model fit parameters."""

        # Set centering value
        cen_val = 100

        # Header
        print('=' * cen_val, '\n')
        print(' FOOOF - PSD MODEL'.center(cen_val), '\n')

        # Frequency range & resolution
        print('The input PSD was modelled in the frequency range {}-{} Hz'.format( \
              self.freq_range[0], self.freq_range[1]).center(cen_val))
        print('Frequency Resolution is {:1.2f} Hz \n'.format(self.freq_res).center(cen_val))

        # Background (slope) parameters
        print('Background Parameters: '.center(100))
        print('{:2.4f}, {:2.4f}, {:2.2e}'.format(self.background_params[0],
                                                 self.background_params[1],
                                                 self.background_params[2]).center(cen_val))

        # Oscillation parameters
        print('\n', '{} oscillations were found:'.format(len(self._gaussian_params)).center(cen_val))
        for op in self._gaussian_params:
            print('CF: {:6.2f}, Amp: {:6.3f}, BW: {:5.2f}'.format(op[0], op[1], op[2]).center(cen_val))

        # Error
        print('\n', 'R-squared error of model fit is {:5.4f}'.format(self.error).center(cen_val))

        # Footer
        print('\n', '=' * cen_val)


    def _quick_background_fit(self, freqs, psd):
        """Fit the 1/f slope of PSD using a linear fit then quadratic fit

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.

        Returns
        -------
        psd_fit : 1d array
            Values of fit slope.
        popt : list of [offset, slope, curvature]
            Parameter estimates.
        """

        # Linear fit - initialize guess with actualy y-intercept, and guess slope of -2
        guess = np.array([psd[0], -2])
        popt, _ = curve_fit(linear_function, freqs, psd, p0=guess)

        # Quadratic fit (using guess parameters from linear fit)
        guess = np.array([popt[0], popt[1], 0])
        popt, _ = curve_fit(quadratic_function, freqs, psd, p0=guess, bounds=self._sl_param_bounds)

        # Calculate the actual oscillation fit
        psd_fit = quadratic_function(freqs, *popt)

        return psd_fit, popt


    def _clean_background_fit(self, freqs, psd):
        """Fit the 1/f slope of PSD using a linear and then quadratic fit, ignoring outliers

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.

        Returns
        -------
        background_fit : 1d array
            Values of fit slope.
        background_params : 1d array
            Parameters of slope fit (length of 3: offset, slope, curvature).

        """

        # Do a quick, initial slope fit
        log_f = np.log10(freqs)
        initial_fit, popt = self._quick_background_fit(log_f, psd)

        # Flatten PSD based on initial slope fit
        psd_flat = psd - initial_fit

        # Remove outliers - any points that drop below 0 (troughs)
        psd_flat[psd_flat < 0] = 0

        # NEW - Amplitude threshold - in terms of # of points
        perc_thresh = np.percentile(psd_flat, self._sl_amp_thresh)
        amp_mask = psd_flat <= perc_thresh
        log_f_ignore = log_f[amp_mask]
        psd_flat_ignore = psd[amp_mask]

        # Second slope fit - using results of first fit as guess parameters
        guess = np.array([popt[0], popt[1], popt[2]])
        background_params, _ = curve_fit(quadratic_function, log_f_ignore, psd_flat_ignore,
                                         p0=guess, bounds=self._sl_param_bounds)

        # Calculate the actual background fit
        background_fit = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))

        return background_fit, background_params


    def _fit_oscs(self, flat_iter):
        """Iteratively fit oscillations to flattened spectrum.

        Parameters
        ----------
        flat_iter : 1d array
            Flattened PSD values.

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].
        """

        guess = np.empty([0, 3])

        # NEW: loop through, checking residuals, stoppind based on STD check
        #  NOTE: depending how good our osc_gauss guesses are, we are 'inducing' residuals
        #   As in - making negative error.
        #     So - with a bad fit, we could add a lot of error, increased STD, and make us stop early
        #       Possibly: stop based on initial STD of flat (unsubtracted) PSD, not an iterative update PSD?
        #   Also: with low variance (no / small 'real' oscillation) this procedure is perhaps overzealous
        #       It finds and fits what we may want to consider small bumps.
        #           Perhaps play with STD val, or add an absolute threshold as well
        while True:

            # Find candidate oscillation
            max_ind = np.argmax(flat_iter)
            max_amp = flat_iter[max_ind]

            # Stop searching for oscillations peaks once drops below amplitude threshold
            if max_amp <= self._amp_std_thresh * np.std(flat_iter):
                break

            # Set the guess parameters for gaussian fitting - CF & Amp
            guess_freq = self.freqs[max_ind]
            guess_amp = max_amp

            # Data driven guess BW
            half_amp = 0.5 * max_amp

            # Find half-amp index on each side of the center frequency
            le_ind = next((x for x in range(max_ind-1, 0, -1) if flat_iter[x] <= half_amp), None)
            ri_ind = next((x for x in range(max_ind+1, len(flat_iter), 1) \
                if flat_iter[x] <= half_amp), None)

            # Keep bandwidth estimation from the shortest side
            #  We grab shortest to avoid >> BW from overalapping oscillations
            # Grab the shortest side, ignoring a side if the half max was not found
            # Note: this will fail if both le & ri ind's end up as None (probably shouldn't happen)
            shortest_side = min([abs(ind-max_ind) for ind in [le_ind, ri_ind] if ind is not None])

            # Estimate BW properly from FWHM
            # Calculate FWHM, converting to Hz
            fwhm = shortest_side * 2 * self.freq_res
            # Calulate guess BW from FWHM
            guess_bw = fwhm / (2 * np.sqrt(2 * np.log(2)))

            # NEW:
            # Check that guess BW isn't outside preset limits - restrict if so
            #  Note: without this, curve_fitting fails if given guess > bounds
            #   Between this, and index search above, covers checking of BWs
            if guess_bw < self.bandwidth_limits[0]:
                guess_bw = self.bandwidth_limits[0]
            if guess_bw > self.bandwidth_limits[1]:
                guess_bw = self.bandwidth_limits[1]

            # Collect guess parameters
            guess = np.vstack((guess, (guess_freq, guess_amp, guess_bw)))

            # Subtract best-guess gaussian
            osc_gauss = gaussian_function(self.freqs, guess_freq, guess_amp, guess_bw)
            flat_iter = flat_iter - osc_gauss

        # Check oscillation based on edges
        keep_osc = self._drop_osc_cf(guess)
        guess = np.array([d for (d, remove) in zip(guess, keep_osc) if remove])

        # Fit oscillations
        _gaussian_params = self._fit_osc_guess(guess)

        # Sort oscillations
        _gaussian_params = _gaussian_params[_gaussian_params[:, 0].argsort()]

        #return guess
        return _gaussian_params


    def _fit_osc_guess(self, guess):
        """Fit a guess of oscillaton gaussian fit.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].

        Returns
        -------
        _gaussian_params : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].
        """

        # Set the bounds, +/- 1 BW for center frequency, positively amp value, and with specified BW limits
        lo_bound = [[osc[0]-osc[2], 0, self.bandwidth_limits[0]] for osc in guess]
        hi_bound = [[osc[0]+osc[2], np.inf, self.bandwidth_limits[1]] for osc in guess]
        gaus_param_bounds = (tuple([item for sublist in lo_bound for item in sublist]), \
                             tuple([item for sublist in hi_bound for item in sublist]))

        # Flatten guess, for use with curve fit
        guess = np.ndarray.flatten(guess)

        # Fit the oscillations
        _gaussian_params, _ = curve_fit(gaussian_function, self.freqs, self._psd_flat,
                                          p0=guess, maxfev=5000, bounds=gaus_param_bounds)

        # Re-organize params into 2d matrix
        _gaussian_params = np.array(group_three(_gaussian_params))

        return _gaussian_params


    def _drop_osc_cf(self, osc_params):
        """Check whether to drop oscillations based CF proximity to edge.

        Parameters
        ----------
        osc_params : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].

        Returns
        -------
        keep_parameter : 1d array, dtype=bool
            Whether to keep each oscillation.
        """

        cf_params = [item[0] for item in osc_params]
        bw_params = [item[2] * self._bw_std_thresh for item in osc_params]

        # Drop if within 1 BW (std. dev) of the edge
        keep_parameter = \
            (np.abs(np.subtract(cf_params, self.freq_range[0])) > bw_params) & \
            (np.abs(np.subtract(cf_params, self.freq_range[1])) > bw_params)

        return keep_parameter


    def _r_squared(self):
        """Calculate r-squared error of the full model fit."""

        self.error = np.sqrt((self.psd - self.psd_fit) ** 2).mean()
