"""FOOOF!

DEPENDENCIES: SCIPY >0.19
"""

import itertools
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from fooof.utils import overlap, group_three, trim_psd
from fooof.funcs import gaussian_function, linear_function, quadratic_function

# TODO:
#   Document inputs: Size, orientation, logged.
#       Notes of linear / logs:
#           Linear / logs:
#               Right now function expects linear frequency and logged powers right? Not sure that's ideal.
#               Suggest: Take both in linear space, big note that this is what's expected (like old foof)
#   Do we have sensible defaults for input parameters?
#       For - number_of_gaussians, window_around_max, bandwidth_limits
#   Variable names & organization (sort out inconsistencies):
#       What get called 'guess' and 'oscillation_params' can vary in organization:
#           Sometimes 2d array, 1d arrays, or list to hold effectively the same info. Can we standardize?
#           Currently the docs are up to date (I think), which shows the inconsistency.
#           Oscillation params is returned as one long list. Group_three before return?
#   Check and potentially clean up the order of the oscillation checks in 'check_oscs'
#           Why is amp out front? Should we check amplitude again after refitting - inside the loop?
#           Should they all be in the loop together?
#   Finish basic, sanity check, test coverage.
#   Clean up object parameters - hide parameters & methods not for direct use.
#   Clear FOOOF object when running new PSD. (It has weird behaviour when re-running without doing so.)

# MAGIC NUMBERS (potentially to be updated, moved to be parameter attributes, or at least doc'd):
#   BW guess (MN-3)
#   Amplitude cut (MN-4)
#   Decision criterion values (MN-5)
#   Edge window in fit_oscs (MN-6)

###################################################################################################
###################################################################################################
###################################################################################################

class FOOOF(object):
    """Model the physiological power spectrum as oscillatory peaks and 1/f background.

    WARNING: INPUT IS LOGGED PSD & LINEAR FREQS (TO FIX, THEN UPDATE WARNING)

    Parameters
    ----------
    number_of_gaussians : int
        Maximum number of oscillations to attempt to fit.
    window_around_max : int
        Frequency window around center frequency to examine.
    bandwidth_limits : list of [float, float]
        Setting to exclude gaussian fits where the bandwidth is implausibly narrow or wide

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the PSD.
    psd : 1d array
        Input power spectral density values.
    frequency_range : list of [float, float]
        Frequency range to process.
    psd_flat : 1d array
        Flattened PSD.
    psd_fit : 1d array
        The full model fit of the PSD - 1/f & oscillations across freq_range.
    background_fit : 1d array
        Values of the background fit.
    oscillation_fit : 1d array
        Values of the oscillation fit (flattened).
    background_params : 1d array
        Parameters that define the background fit.
    oscillation_params : 1d array
        Parameters that define the oscillation (gaussian) fit(s).
    error : float
        R-squared error of the full model fit.

    Notes
    -----
    - Input PSD should be smooth. We recommend ...
    """

    def __init__(self, number_of_gaussians, window_around_max, bandwidth_limits):
        """Initialize FOOOF object with run parameters."""

        # Set input parameters
        self.number_of_gaussians = number_of_gaussians
        self.window_around_max = window_around_max
        self.bandwidth_limits = bandwidth_limits

        ## SETTINGS
        # Noise threshold, as a percentage of the data.
        #  This threshold defines the minimum amplitude, above residuals, to be considered an oscillation
        self._threshold = 0.025
        # Default 1/f parameter bounds. This limits slope to be less than 2 and no steeper than -8.
        self._sl_param_bounds = (-np.inf, -8, 0), (np.inf, 2, np.inf)

        # Initialize all data attributes (to None)
        self._reset_dat()


    def _reset_dat(self):
        """Set (or reset) all data attributes to empty"""

        self.freqs = None
        self.psd = None
        self.psd_flat = None
        self.psd_fit = None
        self.background_fit = None
        self.oscillation_fit = None
        self.background_params = None
        self.oscillation_params = None
        self.error = None


    def model(self, freqs, psd, frequency_range):
        """Run model fit, plot, and print results.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 2d array
            Power spectral density values.
        frequency_range : list of [float, float]
            Desired frequency range to run FOOOF on.
        """

        self.fit(freqs, psd, frequency_range)
        self.plot()
        self.print_params()


    def fit(self, freqs, psd, frequency_range):
        """Fit the full PSD as 1/f and gaussian oscillations.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 2d array
            Power spectral density values.
        frequency_range : list of [float, float]
            Desired frequency range to run FOOOF on.
        """

        # Clear any potentially old data (that could interfere)
        self._reset_dat()

        # Check inputs dimensions & size
        if freqs.ndim != freqs.ndim != 1:
            raise ValueError('Inputs are not 1 dimensional.')
        if freqs.shape != psd.shape:
            raise ValueError('Inputs are not consistent size.')

        # convert window_around_max to freq
        self.window_around_max = np.int(np.ceil(self.window_around_max / (freqs[1]-freqs[0])))

        # Trim the PSD to requested frequency range
        self.frequency_range = frequency_range
        self.freqs, self.psd = trim_psd(freqs, psd, self.frequency_range)

        # Fit the background 1/f
        self.background_params, self.background_fit = self.clean_background_fit(self.freqs, self.psd)

        # Flatten the PSD using fit background
        psd_flat = self.psd - self.background_fit
        psd_flat[psd_flat < 0] = 0
        self.psd_flat = psd_flat

        # Fit initial oscillation gaussian fit
        osc_guess = self.fit_oscs(np.copy(self.psd_flat))

        # Check oscillation guess
        if len(osc_guess) > 0:
            self.oscillation_params = self.check_oscs(osc_guess)
        else:
            self.oscillation_params = []

        #
        if len(self.oscillation_params) > 0:
            self.oscillation_fit = gaussian_function(self.freqs, *self.oscillation_params)
            self.psd_fit = self.oscillation_fit + self.background_fit

        # Logic handle background fit when there are no oscillations
        # ??: Should document / point out you get a different approach to slope fit if no oscillations.
        else:
            log_f = np.log10(self.freqs)
            self.psd_fit, _ = self.quick_background_fit(log_f, self.psd)
            self.oscillation_fit = np.zeros_like(self.freqs)


    def plot(self):
        """Plot the original PSD, and full model fit."""

        plt.plot(self.freqs, self.psd, 'k')
        plt.plot(self.freqs, self.psd_fit, 'g')

        plt.legend(['Original PSD', 'Full model fit'])


    def r_squared(self):
        """Calculate r-squared error of the full model fit."""

        self.error = np.sqrt((self.psd - self.psd_fit) ** 2).mean()


    def print_params(self):
        """Print out the model fit parameters."""

        # Set centering value
        cen_val = 100

        # Header
        print('=' * cen_val, '\n')
        print(' FOOOF - PSD MODEL'.center(cen_val), '\n')

        # Frequency range
        print('The input PSD was modelled in the frequency range: {}-{}'.format( \
              self.frequency_range[0], self.frequency_range[1]).center(cen_val))

        # Background (slope) parameters
        print(self.background_params)

        # Oscillation parameters
        print('\n', '{} oscillations were found'.format(1).center(cen_val), '\n')
        print(self.oscillation_params)

        # Error
        self.r_squared()
        print('\n', 'R-squared error is: {}'.format(self.error).center(cen_val), '\n')

        # Footer
        print('\n', '=' * cen_val)


    def quick_background_fit(self, freqs, psd):
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


    def clean_background_fit(self, freqs, psd):
        """Fit the 1/f slope of PSD using a linear and then quadratic fit, ignoring outliers

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.

        Returns
        -------
        background_params : 1d array
            Parameters of slope fit (length of 3: offset, slope, curvature).
        background_fit : 1d array
            Values of fit slope.
        """

        # Do a quick, initial slope fit
        log_f = np.log10(freqs)
        quadratic_fit, popt = self.quick_background_fit(log_f, psd)

        # Flatten PSD based on initial slope fit
        psd_flat = psd - quadratic_fit

        # Remove outliers - any points that drop below 0 (troughs)
        psd_flat[psd_flat < 0] = 0

        # Amplitude threshold - in terms of % of power
        #amplitude_threshold = np.max(psd_flat) * self._threshold
        #amp_mask = psd_flat <= (amplitude_threshold)
        #log_f_ignore = log_f[amp_mask]
        #psd_flat_ignore = psd[amp_mask]

        # NEW - Amplitude threshold - in terms of # of points
        perc_thresh = np.percentile(psd_flat, self._threshold)
        amp_mask = psd_flat <= perc_thresh
        log_f_ignore = log_f[amp_mask]
        psd_flat_ignore = psd[amp_mask]

        # Second slope fit - using results of first fit as guess parameters
        guess = np.array([popt[0], popt[1], popt[2]])
        background_params, _ = curve_fit(quadratic_function, log_f_ignore, psd_flat_ignore,
                                         p0=guess, bounds=self._sl_param_bounds)

        # Calculate the actual background fit
        background_fit = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))

        return background_params, background_fit


    def fit_oscs(self, flat_iteration):
        """Iteratively fit oscillations to flattened spectrum.

        Parameters
        ----------
        flat_iteration : 1d array
            Flattened PSD values.

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].
        """

        gausi = 0
        guess = np.empty((0, 3))

        #
        while gausi < self.number_of_gaussians:
            max_index = np.argmax(flat_iteration)
            max_amp = flat_iteration[max_index]

            # trim gaussians at the edges of the PSD
            # trimming these here dramatically speeds things up, since the trimming later...
            # ... requires doing the gaussian curve fitting, which is slooow
            cut_freq = [0, 0]

            # MN-6
            edge_window = 1.

            cut_freq[0] = np.int(np.ceil(self.frequency_range[0]/(self.freqs[1]-self.freqs[0])))
            cut_freq[1] = np.int(np.ceil(self.frequency_range[1]/(self.freqs[1]-self.freqs[0])))
            drop_cond1 = (max_index - edge_window) <= cut_freq[0]
            drop_cond2 = (max_index + edge_window) >= cut_freq[1]
            drop_criterion = drop_cond1 | drop_cond2

            if ~drop_criterion:

                # MN-3
                # set the guess parameters for gaussian fitting (bw = 2)
                guess_freq = self.freqs[max_index]
                guess_amp = max_amp
                guess_bw = 2.
                guess = np.vstack((guess, (guess_freq, guess_amp, guess_bw)))

                # flatten the flat PSD around this peak
                flat_range = ((max_index-self.window_around_max), (max_index+self.window_around_max))
                flat_iteration[flat_range[0]:flat_range[1]] = 0

            # flatten edges if the "peak" is at the edge (but don't store that as a gaussian to fit)
            if drop_cond1:
                flat_range = (0, (max_index+self.window_around_max))
                flat_iteration[flat_range[0]:flat_range[1]] = 0

            if drop_cond2:
                flat_range = ((max_index-self.window_around_max), self.frequency_range[1])
                flat_iteration[flat_range[0]:flat_range[1]] = 0

            gausi += 1

        return guess


    def check_oscs(self, guess):
        """Check oscillation parameters meet inclusion criteria.

        Parameters
        ----------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].

        Returns
        -------
        oscillation_params : 1d array
            Gaussian definition for oscillation fit: triplets of [center freq, amplitude, bandwidth].
        """

        # Remove gaussians with low amplitude
        #  NOTE: Why don't we move this to the fit_oscs method? It works on the guess.
        keep_osc = self._drop_osc_amp(guess)
        guess = [d for (d, remove) in zip(guess, keep_osc) if remove]

        # Fit a guess of oscillations parameters
        oscillation_params = self._fit_osc_guess(guess)

        # iterate through gaussian fitting to remove implausible oscillations
        keep_osc = False
        while ~np.all(keep_osc):

            # remove gaussians by cf and bandwidth
            osc_params = group_three(oscillation_params)
            keep_osc = np.logical_and(self._drop_osc_cf(osc_params), self._drop_osc_bw(osc_params))

            guess = [d for (d, remove) in zip(osc_params, keep_osc) if remove]

            # Remove oscillations due to BW overlap (one osc is entirely within another)
            guess = self._drop_osc_overlap(guess)

            # Refit oscillation guess
            if len(guess) > 0:
                oscillation_params = self._fit_osc_guess(guess)

            # Break out of loop, and set empty params, if no oscillations are found
            else:
                oscillation_params = []
                break

        return oscillation_params


    def _fit_osc_guess(self, guess):
        """Fit a guess of oscillaton gaussian fit.

        Parameters
        ----------
        guess : list of 1d array of [CF, AMP, BW]
            Guess parameters for gaussian oscillation fits.

        Returns
        -------
        oscillation_params : 1d array
            Gaussian definition for oscillation fit: triplets of [center freq, amplitude, bandwidth].
        """

        # set the parameter bounds for the gaussians
        lo_bound = self.frequency_range[0], 0, self.bandwidth_limits[0]
        hi_bound = self.frequency_range[1], np.inf, self.bandwidth_limits[1]

        #
        num_of_oscillations = int(np.shape(guess)[0])
        guess = list(itertools.chain.from_iterable(guess))
        gaus_param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations
        oscillation_params, _ = curve_fit(gaussian_function, self.freqs, self.psd_flat,
                                          p0=guess, maxfev=5000, bounds=gaus_param_bounds)

        return oscillation_params


    def _drop_osc_amp(self, osc_params):
        """Check whether to drop oscillations based on low amplitude.

        Parameters
        ----------
        osc_params : 2d array
            Gaussian definition for oscillation fit, each row: [CF, AMP, BW].

        Returns
        -------
        keep_parameter : 1d array, dtype=bool
            Whether to keep each oscillation.
        """

        amp_params = [item[1] for item in osc_params]

        # MN-4
        amp_cut = 0.5 * np.var(self.psd_flat)

        keep_parameter = amp_params > amp_cut

        return keep_parameter


    def _drop_osc_cf(self, osc_params):
        """Check whether to drop oscillations based on center frequencies.

        Parameters
        ----------
        osc_params : 2d array
            Gaussian definition for oscillation fit, each row: [CF, AMP, BW].

        Returns
        -------
        keep_parameter : 1d array, dtype=bool
            Whether to keep each oscillation.
        """

        cf_params = [item[0] for item in osc_params]

        keep_parameter = \
            (np.abs(np.subtract(cf_params, self.frequency_range[0])) > 2) & \
            (np.abs(np.subtract(cf_params, self.frequency_range[1])) > 2)

        return keep_parameter


    def _drop_osc_bw(self, osc_params):
        """Check whether to drop oscillations based on bandwidths.

        Parameters
        ----------
        osc_params : 2d array
            Gaussian definition for oscillation fit, each row: [CF, AMP, BW].

        Returns
        -------
        keep_parameter : 1d array, dtype=bool
            Whether to keep each oscillation.
        """

        bw_params = [item[2] for item in osc_params]

        keep_parameter = \
            (np.abs(np.subtract(bw_params, self.bandwidth_limits[0])) > 10e-4) & \
            (np.abs(np.subtract(bw_params, self.bandwidth_limits[1])) > 10e-4)

        return keep_parameter


    def _drop_osc_overlap(self, osc_params):
        """Drop oscillation definitions if they are entirely within another oscillation.

        Parameters
        ----------
        osc_params : list of lists of [float, float, float]
            Gaussian definition for oscillation fit, each list: [CF, AMP, BW].

        Returns
        -------
        oscs : list of lists of [float, float, float]
            Gaussian definition for oscillation fit, each list: [CF, AMP, BW].
        """

        n_oscs = len(osc_params)

        oscs = sorted(osc_params, key=lambda x: float(x[2]))
        bounds = [[osc[0]-osc[2], osc[0]+osc[2]] for osc in oscs]

        drops = []
        for i, bound in enumerate(bounds[:-1]):
            for j in range(i+1, n_oscs):
                if overlap(bound, bounds[j]):

                    # Mark overlapped oscillation to be dropped
                    drops.append(i)

        oscs = [oscs[k] for k in list(set(range(n_oscs)) - set(drops))]

        return sorted(oscs)
