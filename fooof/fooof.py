"""FOOOF!

DEPENDENCIES: SCIPY >0.19
"""

import itertools
import numpy as np
from scipy.optimize import curve_fit

from fooof.utils import overlap, group_three, get_index_from_vector, trim_psd
from fooof.funcs import gaussian_function, linear_function, quadratic_function


# TODO:
#   Make I/O order for parameters consistent
#       Note - order: freqs, psd
#   Final call on size / shape of PSD inputs (take 1 or many?)
#       Then:   - fix up size checking.
#               - document conventions for inputs
#   Document inputs: Size, orientation, logged.
#   Do we have sensible defaults for input parameters?
#       For - number_of_gaussians, window_around_max, bandwidth_limits
#   Which slope fitting do we want exposed? Potentially hide the other, change names.
#   Add basic plotting function to display PSD & Fit?

# MAGIC NUMBERS:
#   threshold amplitude (MN-1)
#   1/f parameter bounds (MN-2)
#   BW guess (MN-3)
#   Amplitude cut (MN-4)
#   Decision criterion values (MN-5)
#   Edge window in fit_oscs (MN-6)
#   Guess params in quick_fit (MN-7)

# NOTES:
#   Size of PSD inputs:
#     Since all we do is average, what is the benefit of taking multiple PSDs?
#       Since we only ever fit 1, could add a note to average before FOOOF, if user wants
#   Linear / logs:
#     Right now function expects linear frequency and logged powers right? Not sure that's ideal.
#       Suggest: Take both in linear space, big note that this is what's expected (like old foof)
#   Right now it reduces to requested range, and only stores trimmed psd & freqs. Change?
#       It used to keep psd & trimmed_psd, but only trimmed freqs. Whichever - needs to be consistent.
#   What does the 'p' stand for in flattened slope vars?
#   What get called 'guess' and 'oscillation_params' can vary in organization:
#       Sometimes 2d array, 1d arrays, or list to hold effectively the same info. Can we standardize?
#       Currently the docs are up to date (I think), which shows the inconsistency.

###################################################################################################
###################################################################################################
###################################################################################################


class FOOOF(object):
    """Model the physiological power spectrum as oscillatory peaks and 1/f background.

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
    psd : 2d array
        Input power spectral density values.
    frequency_range : list of [float, float]
        Frequency range to process.
    p_flat_real : 1d array
        Flattened PSD.
    psd_fit : 1d array
        The full model fit of the PSD - 1/f & oscillations across freq_range.
    background_fit : 1d array
        Values of the background fit.
    gaussian_fit : 1d array
        Values of the oscillation fit (flattened).
    background_params : 1d array
        Parameters that define the background fit: [TODO: WHAT ARE THEY!?]
    oscillation_params : 1d array
        Parameters that define the oscillation (gaussian) fit(s).
    """

    def __init__(self, number_of_gaussians, window_around_max, bandwidth_limits):
        """Initialize FOOOF object with run parameters."""

        # Set input parameters
        self.number_of_gaussians = number_of_gaussians
        self.window_around_max = window_around_max
        self.bandwidth_limits = bandwidth_limits

        # MN-1
        # outlier amplitude is also the minimum amplitude required for counting as an "oscillation"
        # this is express as percent relative maximum oscillation height
        self.threshold = 0.025
        # MN-2
        # default 1/f parameter bounds limit slope to be less than 2 and no steeper than -8
        self.param_bounds = (-np.inf, -8, 0), (np.inf, 2, np.inf)

        # Initialize all other attributes
        self.freqs = None
        self.psd = None
        self.p_flat_real = None
        self.psd_fit = None
        self.background_fit = None
        self.gaussian_fit = None    # NOTE: rename oscillation fit, for consistency with other names?
        self.background_params = None
        self.oscillation_params = None


    def fit(self, freqs, input_psd, frequency_range):
        """Fit the full PSD as 1/f and gaussian oscillations.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        input_psd : 2d array
            Power spectral density values.
        frequency_range : list of [float, float]
            Desired frequency range to run FOOOF on.
        """

        # Check dimensions
        if input_psd.ndim > 2:
            raise ValueError("input PSD must be 1- or 2- dimensional")

        # convert window_around_max to freq
        self.window_around_max = np.int(np.ceil(self.window_around_max / (freqs[1]-freqs[0])))

        # trim the PSD
        self.frequency_range = frequency_range
        self.freqs, foof_spec = trim_psd(freqs, input_psd, self.frequency_range)

        # Check dimensions
        if np.shape(self.freqs)[0] == np.shape(foof_spec)[0]:
            foof_spec = foof_spec.T

        # Average across all provided PSDs
        # NOTE: Why NaN mean? Do we expect NaNs? What happens if they are there?
        #    Should we check inputs to exclude NaNs first?
        self.psd = np.nanmean(foof_spec, 0)

        # Fit the background 1/f
        self.background_params, self.background_fit = self.clean_background_fit(self.freqs, self.psd)
                                                                 #self.threshold, self.param_bounds)

        # Flatten the PSD using fit background
        p_flat_real = self.psd - self.background_fit
        p_flat_real[p_flat_real < 0] = 0
        self.p_flat_real = p_flat_real
        #p_flat_iteration = np.copy(p_flat_real)

        # Fit initial oscillation gaussian fit
        osc_guess = self.fit_oscs(np.copy(self.p_flat_real))

        # Check oscillation guess
        if len(osc_guess) > 0:
            self.oscillation_params = self.check_oscs(osc_guess)
        else:
            self.oscillation_params = []

        #
        if len(self.oscillation_params) > 0:
            self.gaussian_fit = gaussian_function(self.freqs, *self.oscillation_params)
            self.psd_fit = self.gaussian_fit + self.background_fit

        # Logic handle background fit when there are no oscillations
        else:
            log_f = np.log10(self.freqs)
            self.psd_fit, _ = self.quick_background_fit(log_f, self.psd)#, self.param_bounds)
            self.gaussian_fit = np.zeros_like(self.freqs)

        #return p_flat_real, freqs, trimmed_psd, psd_fit, background_fit, gaussian_fit, background_params, oscillation_params


    def quick_background_fit(self, freqs, psd): #, param_bounds):
        """Fit the 1/f slope of PSD using a linear fit then quadratic fit

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.

        # NOW OBJECT ATTRIBUTE
        param_bounds : list of [float, float, float]
            Guess parameters for fitting the quadratic 1/f

        Returns
        -------
        psd_fit : 1d array
            Values of fit slope.
        popt : list of [offset, slope, curvature]
            Parameter estimates.
        """

        # MN-7
        # Linear fit
        guess = np.array([psd[0], -2])
        popt, _ = curve_fit(linear_function, freqs, psd, p0=guess)

        # Quadratic fit (using guess parameters from linear fit)
        guess = np.array([popt[0], popt[1], 0])
        popt, _ = curve_fit(quadratic_function, freqs, psd, p0=guess, bounds=self.param_bounds)

        psd_fit = quadratic_function(freqs, *popt)

        return psd_fit, popt


    def clean_background_fit(self, freqs, psd): #, threshold, param_bounds):
        """Fit the 1/f slope of PSD using a linear and then quadratic fit, ignoring outliers

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the PSD.
        psd : 1d array
            Power spectral density values.

        # NOW OBJECT ATTRIBUTES
        threshold : scalar
            Threshold for removing outliers during fitting.
        param_bounds : list of [float, float, float]
            Guess parameters for fitting the quadratic 1/f

        Returns
        -------
        background_params : 1d array
            Parameters of slope fit (length of 3: offset, slope, curvature).
        background_fit : 1d array
            Values of fit slope.
        """

        log_f = np.log10(freqs)
        quadratic_fit, popt = self.quick_background_fit(log_f, psd)#, self.param_bounds)
        p_flat = psd - quadratic_fit

        # remove outliers
        p_flat[p_flat < 0] = 0
        amplitude_threshold = np.max(p_flat) * self.threshold
        cutoff = p_flat <= (amplitude_threshold)
        log_f_ignore = log_f[cutoff]
        p_ignore = psd[cutoff]

        # use the outputs from the first fit as the guess for the second fit
        guess = np.array([popt[0], popt[1], popt[2]])
        background_params, _ = curve_fit(quadratic_function, log_f_ignore, p_ignore,
                                         p0=guess, bounds=self.param_bounds)
        background_fit = background_params[0] + (background_params[1]*(log_f)) + (background_params[2]*(log_f**2))

        return background_params, background_fit


    def fit_oscs(self, p_flat_iteration):
        """Iteratively fit oscillations to flattened spectrum.

        Parameters
        ----------
        p_flat_iteration : 1d array
            Flattened PSD values.

        Returns
        -------
        guess : 2d array
            Guess parameters for gaussian fits to oscillations. [n_oscs, 3], row: [CF, AMP, BW].
        """

        guess = np.empty((0, 3))
        gausi = 0

        #
        while gausi < self.number_of_gaussians:
            max_index = np.argmax(p_flat_iteration)
            max_amp = p_flat_iteration[max_index]

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
                p_flat_iteration[flat_range[0]:flat_range[1]] = 0

            # flatten edges if the "peak" is at the edge (but don't store that as a gaussian to fit)
            if drop_cond1:
                flat_range = (0, (max_index+self.window_around_max))
                p_flat_iteration[flat_range[0]:flat_range[1]] = 0

            if drop_cond2:
                flat_range = ((max_index-self.window_around_max), self.frequency_range[1])
                p_flat_iteration[flat_range[0]:flat_range[1]] = 0

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

        NOTE: need to sanity check which checks are done where (order).
            Why is amp out front?
            Should they all be in the loop?
        """

        # Remove gaussians with low amplitude
        # NOTE: is there a reason we do this here, and not again after refitting?
        #  Should we check amplitide inside the while loop as well?
        keep_osc = self._drop_osc_amp(guess)
        guess = [d for (d, remove) in zip(guess, keep_osc) if remove]

        # SAME AS ABOVE: OLD VERSION
        # remove low amplitude gaussians
        # MN-4
        #amp_cut = 0.5 * np.var(p_flat_real)
        #amp_params = [item[1] for item in guess]
        #keep_osc = amp_params > amp_cut

        # Fit a guess of oscillations parameters
        oscillation_params = self._fit_osc_guess(guess)

        # SAME AS ABOVE: OLD VERSION
        #num_of_oscillations = int(np.shape(guess)[0])
        #guess = list(itertools.chain.from_iterable(guess))

        # make a list of the bounds to pass into the curve fitting
        #gaus_param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations
        #try:
        #oscillation_params, _ = curve_fit(gaussian_function, freqs, p_flat_real,
        #                                  p0=guess, maxfev=5000, bounds=gaus_param_bounds)
        #except:
        #   oscillation_params = []
        #    pass

        # iterate through gaussian fitting to remove implausible oscillations
        keep_osc = False
        while ~np.all(keep_osc):

            # remove gaussians by cf and bandwidth
            osc_params = group_three(oscillation_params)
            keep_osc = np.logical_and(self._drop_osc_cf(osc_params), self._drop_osc_bw(osc_params))

            # SAME AS ABOVE (OLD VERSION):
            #osc_params = group_three(oscillation_params)
            #cf_params = [item[0] for item in osc_params]
            #bw_params = [item[2] for item in osc_params]
            #keep_osc = self._decision_criterion(cf_params, bw_params, frequency_range, bandwidth_limits)

            guess = [d for (d, remove) in zip(osc_params, keep_osc) if remove]

            # Remove oscillations due to BW overlap (one osc is entirely within another)
            guess = self._drop_osc_overlap(guess)

            # Refit oscillation guess
            if len(guess) > 0:
                oscillation_params = self._fit_osc_guess(guess)

            # SAME AS ABOVE: OLD VERSION
            #if len(guess) > 0:
            #    num_of_oscillations = int(np.shape(guess)[0])
            #    guess = list(itertools.chain.from_iterable(guess))
            #    gaus_param_bounds = lo_bound*num_of_oscillations, hi_bound*num_of_oscillations
            #    oscillation_params, _ = curve_fit(gaussian_function, freqs, p_flat_real,
            #                                      p0=guess, maxfev=5000, bounds=gaus_param_bounds)

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
        oscillation_params, _ = curve_fit(gaussian_function, self.freqs, self.p_flat_real,
                                          p0=guess, maxfev=5000, bounds=gaus_param_bounds)

        return oscillation_params


    # NOTE: below was split out for more explicit / modular decision criteria.
    #def _decision_criterion(self, cf_params, bw_params, frequency_range, bandwidth_limits):
        """Decide whether a potential oscillation fit meets criterion.

        Parameters
        ----------


        Returns
        -------
        keep_parameter : boolean
            Whether the oscillation fit is deemed appropriate to keep.

        Notes
        -----
        # decision criteria for keeping fitted oscillations
        # std of gaussian fit needs to not be too narrow...
        # ... nor too wide
        # and cf of oscillation can't be too close to edges,
        #   else there's not enough infomation to make a good fit
        """

    #    lo_bw = self.bandwidth_limits[0]
    #    hi_bw = self.bandwidth_limits[1]

        # MN-5
    #    keep_parameter = \
    #        (np.abs(np.subtract(cf_params, frequency_range[0])) > 2) & \
    #        (np.abs(np.subtract(cf_params, frequency_range[1])) > 2) & \
    #        (np.abs(np.subtract(bw_params, lo_bw)) > 10e-4) & \
    #        (np.abs(np.subtract(bw_params, hi_bw)) > 10e-4)

    #    return keep_parameter


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
        amp_cut = 0.5 * np.var(self.p_flat_real)

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
                    # print('DROPPED')
                    drops.append(i)

                    # NOTE: in a small number of manual test cases, it doesn't
                    #  matter if you use either or neither of the updates below,
                    #  the end fit ends up exactly the same.

                    # Update parameters for overlapping osc
                    #  New CF is combined across each, weighted by amp
                    #oscs[i][0] = oscs[i][0] * (oscs[i][1] / oscs[i][1] + oscs[j][1]) + \
                    #             oscs[j][0] * (oscs[j][1] / oscs[j][1] + oscs[j][1])

                    # Or - update CF and Amp to straight average
                    #oscs[i][0] = (oscs[i][0] + oscs[j][0]) / 2
                    #oscs[i][1] = (oscs[i][1] + oscs[j][1]) / 2

        oscs = [oscs[k] for k in list(set(range(n_oscs)) - set(drops))]

        return sorted(oscs)
