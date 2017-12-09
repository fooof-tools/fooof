"""FOOOF - Fitting Oscillations & One-Over F."""

import os
import io
import json
import warnings
from collections import namedtuple

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from scipy.optimize import curve_fit

from fooof.utils import trim_psd, mk_freq_vector
from fooof.utils import group_three, get_attribute_names, check_array_dim
from fooof.utils import dict_array_to_lst, dict_select_keys, dict_lst_to_array
from fooof.funcs import gaussian_function, expo_function, expo_nk_function

###################################################################################################
###################################################################################################

FOOOFResult = namedtuple('FOOOFResult', ['background_params', 'oscillation_params',
                                         'r2', 'error', 'gaussian_params'])

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

    Notes
    -----
    Input PSD should be smooth - overly noisy power spectra may lead to bad fits.
        - In particular, raw FFT inputs are not appropriate, we recommend using either Welch's
        procedure, or a median filter smoothing on the FFT output before running FOOOF.
        - Where possible and appropriate, use longer time segments for PSD calculation to
        get smoother PSDs; this will give better FOOOF fits.
    If using the FOOOFGroup Object, all parameters and attributes are the same.
        - The main addition is 'group_results', which stores FOOOF results across the group of PSDs.
    """

    def __init__(self, bandwidth_limits=(0.5, 12.0), max_n_oscs=np.inf,
                 min_amp=0.0, amp_std_thresh=2.0, bg_use_knee=False, verbose=True):
        """Initialize FOOOF object with run parameters."""

        # Set input parameters
        self.bg_use_knee = bg_use_knee
        self.bandwidth_limits = bandwidth_limits
        self.max_n_oscs = max_n_oscs
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
        self._reset_dat()


    def _reset_settings(self):
        """Set (or reset) internal settings, based on what is provided in init.

        Notes
        -----
        These settings are for interal use, based on what is provided to, or set in init.
            They should not be altered by the user.
        """

        # Set exponential function version for whether fitting knee or not
        self._bg_fit_func = expo_function if self.bg_use_knee else expo_nk_function
        # Bandwidth limits are given in 2-sided oscillation bandwidth.
        #  Convert to gaussian std parameter limits.
        self._std_limits = [bwl / 2 for bwl in self.bandwidth_limits]
        # Bounds for background fitting. Drops bounds on knee parameter if not set to fit knee
        self._bg_bounds = self._bg_bounds if self.bg_use_knee \
            else tuple(bound[0::2] for bound in self._bg_bounds)


    def _reset_dat(self, clear_freqs=True):
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


    @classmethod
    def from_group(cls, fg, ind, regenerate=False):
        """Initialize a FOOOF object from specified data in a FOOOFGroup object.

        Parameters
        ----------
        fg : FOOOFGroup() object
            An object with FOOOFResults available.
        ind : int
            The index of the FOOOFResult in FOOOFGroup.group_results to load.

        Returns
        -------
        inst : FOOOF() object
            The FOOOFResult data loaded into a FOOOF object.
        """

        # Initialize instance, inheriting settings from FOOOFGroup object, and copy over frequency information
        inst = cls(fg.bandwidth_limits, fg.max_n_oscs, fg.min_amp, fg.amp_std_thresh, fg.bg_use_knee, fg.verbose)
        inst.freq_range, inst.freq_res = fg.freq_range, fg.freq_res
        inst.freqs = mk_freq_vector(inst.freq_range, inst.freq_res)

        # Add results data from specified FOOOFResult, copy over frequency information, and infer knee
        inst.add_results(fg.group_results[ind], regenerate=regenerate)

        return inst


    def add_data(self, freqs, psd, freq_range=None, reset_dat=True):
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
        #  Note: this option is for internal use (called from FOOOFGroup)
        #    It assumes the PSD is already logged, with correct freq_range.
        elif isinstance(psd, np.ndarray):
            self.psd = psd

        # Check that data is available
        if not (np.all(self.freqs) and np.all(self.psd)):
            raise ValueError('No data available to fit - can not proceed.')

        # Check bandwidth limits against frequency resolution; warn if too close.
        if 1.5 * self.freq_res >= self.bandwidth_limits[0] and self.verbose:
            print("\nFOOOF WARNING: Lower-bound bandwidth limit is < or ~= the frequency resolution: {:1.2f} <= {:1.2f}\
                  \n\tLower bounds below frequency-resolution have no effect (effective lower bound is freq-res)\
                  \n\tToo low a limit may lead to overfitting noise as small bandwidth oscillations.\
                  \n\tWe recommend a lower bound of approximately 2x the frequency resolution.\n".format(self.freq_res, self.bandwidth_limits[0]))

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


    def plot(self, plt_log=False, save_fig=False, save_name='FOOOF_fit', save_path='', ax=None):
        """Plot the original PSD, and full model fit.

        Parameters
        ----------
        plt_log : boolean, optional
            Whether or not to plot the frequency axis in log space. default: False
        save_fig : boolean, optional
            Whether to save out a copy of the plot. default : False
        save_name : str, optional
            Name to give the saved out file.
        save_path : str, optional
            Path to directory in which to save. If not provided, saves to current directory.
        ax : matplotlib.Axes, optional
            Figure axes upon which to plot.
        """

        if not np.all(self.freqs):
            raise ValueError('No data available to plot - can not proceed.')

        # Set frequency vector, logged if requested
        plt_freqs = np.log10(self.freqs) if plt_log else self.freqs

        # Create plot axes, if not provided
        if not ax:
            fig, ax = plt.subplots(figsize=(12, 10))

        # Create the plot
        if np.all(self.psd):
            ax.plot(plt_freqs, self.psd, 'k', linewidth=1.0, label='Original PSD')
        if np.all(self.psd_fit_):
            ax.plot(plt_freqs, self.psd_fit_, 'r', linewidth=3.0,
                    alpha=0.5, label='Full model fit')
            ax.plot(plt_freqs, self._background_fit, '--b', linewidth=3.0,
                    alpha=0.5, label='Background fit')

        ax.set_xlabel('Frequency', fontsize=20)
        ax.set_ylabel('Power', fontsize=20)
        ax.tick_params(axis='both', which='major', labelsize=16)

        ax.legend(prop={'size': 16})
        ax.grid()

        # Save out figure, if requested
        if save_fig:
            plt.savefig(os.path.join(save_path, save_name + '.png'))


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


    def print_results(self):
        """Print out FOOOF results."""

        print(self._gen_results_str())


    def get_results(self):
        """Return model fit parameters and error."""

        return FOOOFResult(self.background_params_, self.oscillation_params_, self.r2_,
                           self.error_, self._gaussian_params)


    def create_report(self, save_name='FOOOF_Report', save_path='', plt_log=False):
        """Generate and save out a report of the current FOOOF fit.

        Parameters
        ----------
        save_name : str, optional
            Name to give the saved out file.
        save_path : str, optional
            Path to directory in which to save. If not provided, saves to current directory.
        plt_log : bool, optional
            Whether or not to plot the frequency axis in log space. default: False
        """

        # Set the font description for saving out text with matplotlib
        font = {'family': 'monospace',
                'weight': 'normal',
                'size': 16}

        # Set up outline figure, using gridspec
        fig = plt.figure(figsize=(16, 20))
        grid = gridspec.GridSpec(3, 1, height_ratios=[0.8, 1.0, 0.7])

        # First - text results
        ax0 = plt.subplot(grid[0])
        results_str = self._gen_results_str()
        ax0.text(0.5, 0.2, results_str, font, ha='center')
        ax0.set_frame_on(False)
        ax0.set_xticks([])
        ax0.set_yticks([])

        # Second - data plot
        ax1 = plt.subplot(grid[1])
        self.plot(plt_log=plt_log, ax=ax1)

        # Third - FOOOF settings
        ax2 = plt.subplot(grid[2])
        settings_str = self._gen_settings_str(False)
        ax2.text(0.5, 0.2, settings_str, font, ha='center')
        ax2.set_frame_on(False)
        ax2.set_xticks([])
        ax2.set_yticks([])

        # Save out the report
        plt.savefig(os.path.join(save_path, save_name + '.pdf'))
        plt.close()


    def save(self, save_file='fooof_dat', save_path='', save_results=False,
             save_settings=False, save_data=False, append=False):
        """Save out data, results and/or settings from FOOOF object. Saves out to a JSON file.

        Parameters
        ----------
        save_file : str or FileObject, optional
            File to which to save data.
        save_path : str
            Path to directory to which the save. If not provided, saves to current directory.
        save_results : bool, optional
            Whether to save out FOOOF model fit results.
        save_settings : bool, optional
            Whether to save out FOOOF settings.
        save_data : bool, optional
            Whether to save out input data.
        append : bool, optional
            Whether to append to an existing file, if available. default: False
                This option is only valid (and only used) if save_file is a str.
        """

        # Get dictionary of all attributes
        attributes = get_attribute_names()

        # Convert object to dictionary & convert all arrays to lists - for JSON serializing
        obj_dict = dict_array_to_lst(self.__dict__)

        # Set which variables to keep. Use a set to drop any potential overlap
        keep = set((attributes['results'] if save_results else []) + \
                   (attributes['settings'] if save_settings else []) + \
                   (attributes['dat'] if save_data else []))

        # Keep only requested vars
        obj_dict = dict_select_keys(obj_dict, keep)

        # Save out - create new file, (creates a JSON file)
        if isinstance(save_file, str) and not append:
            with open(os.path.join(save_path, save_file + '.json'), 'w') as outfile:
                json.dump(obj_dict, outfile)

        # Save out - append to file_name (appends to a JSONlines file)
        if isinstance(save_file, str) and append:
            with open(os.path.join(save_path, save_file + '.json'), 'a') as outfile:
                json.dump(obj_dict, outfile)
                outfile.write('\n')

        # Save out - append to given file object (appends to a JSONlines file)
        elif isinstance(save_file, io.IOBase):
            json.dump(obj_dict, save_file)
            save_file.write('\n')


    def load(self, load_file='fooof_dat', file_path=''):
        """Load in FOOOF file. Reads in a JSON file.

        Parameters
        ----------
        load_file : str or FileObject, optional
            File from which to load data.
        file_path : str
            Path to directory from which to load. If not provided, loads from current directory.
        """

        # Load data from file
        if isinstance(load_file, str):
            with open(os.path.join(file_path, load_file + '.json'), 'r') as infile:
                dat = json.load(infile)
        elif isinstance(load_file, io.IOBase):
            dat = json.loads(load_file.readline())

        # Reset data in object, so old data can't interfere
        self._reset_dat()

        # Get dictionary of available attributes, and convert specified lists back into arrays
        attributes = get_attribute_names()
        dat = dict_lst_to_array(dat, attributes['arrays'])

        # Reconstruct FOOOF object
        for key in dat.keys():
            setattr(self, key, dat[key])

        # If settings not loaded from file, clear from object, so that default
        #  settings, which are potentially wrong for loaded data, aren't kept
        if not set(attributes['settings']).issubset(set(dat.keys())):
            self._clear_settings()

            # Infer whether knee fitting was used, if background params have been loaded
            if np.all(self.background_params_):
                self._infer_knee()

        # Otherwise (settings were loaded), reset internal settings so that they are consistent
        else:
            self._reset_settings()

        # If results loaded, check dimensions of osc/gauss parameters
        #  This fixes an issue where they end up the wrong shape if they are empty (no oscs)
        if set(attributes['results']).issubset(set(dat.keys())):
            self.oscillation_params_ = check_array_dim(self.oscillation_params_)
            self._gaussian_params = check_array_dim(self._gaussian_params)

        # Reconstruct frequency vector, if data available to do so
        if self.freq_res:
            self.freqs = mk_freq_vector(self.freq_range, self.freq_res)

        # Recreate PSD model & components
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


    def _create_osc_fit(self, freqs, gaus_params):
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
            Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].

        Returns
        -------
        oscillation_params :  2d array
            Fitted parameter values for the oscillations. Each row is an oscillation, as [CF, Amp, BW].

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

        for i, osc in enumerate(gaus_params):

            # Gets the index of the PSD at the frequency closest to the CF of the osc
            ind = min(range(len(self.freqs)), key=lambda i: abs(self.freqs[i] - osc[0]))

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
            Power spectral density values, in linear space. Either 1d vector, or 2d as [n_psds, n_freqs].
        freq_range :
            Frequency range to restrict PSD to. If None, keeps the entire range.
        verbose : bool, optional
            Whether to be verbose in printing out warnings.

        Returns
        -------
        freqs : 1d array
            Frequency values for the PSD, in linear space.
        psd : 1d or 2d array
            Power spectral density values, in linear space. Either 1d vector, or 2d as [n_psds, n_freqs].
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
                print('\nFOOOF WARNING: Skipping frequency == 0, as this causes problem with fitting.')

        # Calculate frequency resolution, and actual frequency range of the data
        freq_range = [freqs.min(), freqs.max()]
        freq_res = freqs[1] - freqs[0]

        # Log power values
        psd = np.log10(psd)

        return freqs, psd, freq_range, freq_res


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
        desc = {'bg_use_knee' : 'Whether to fit a knee parameter in background fitting.',
                'bw_lims'     : 'Possible range of bandwidths for extracted oscillations, in Hz.',
                'num_oscs'    : 'The maximum number of oscillations that can be extracted.',
                'min_amp'     : "Minimum absolute amplitude, above background, "
                                "for an oscillation to be extracted.",
                'amp_thresh'  : "Threshold, in units of standard deviation,"
                                "at which to stop searching for oscillations."}

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
            *[el for el in ['Fit Knee : {}'.format(self.bg_use_knee).center(cen_val),
                            '{}'.format(desc['bg_use_knee']).center(cen_val),
                            'Bandwidth Limits : {}'.format(self.bandwidth_limits).center(cen_val),
                            '{}'.format(desc['bw_lims']).center(cen_val),
                            'Max Number of Oscillations : {}'.format(self.max_n_oscs).center(cen_val),
                            '{}'.format(desc['num_oscs']).center(cen_val),
                            'Minimum Amplitude : {}'.format(self.min_amp).center(cen_val),
                            '{}'.format(desc['min_amp']).center(cen_val),
                            'Amplitude Threshold: {}'.format(self.amp_std_thresh).center(cen_val),
                            '{}'.format(desc['amp_thresh']).center(cen_val)] if el != ' '*cen_val],

            # Footer
            '',
            '=' * cen_val
        ])

        return output


    def _gen_results_str(self):
        """Generate a string representation of model fit results."""

        if not np.all(self.background_params_):
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
                int(np.floor(self.freq_range[0])), int(np.ceil(self.freq_range[1]))).center(cen_val),
            'Frequency Resolution is {:1.2f} Hz'.format(self.freq_res).center(cen_val),
            '',

            # Background parameters
            ('Background Parameters (offset, ' + ('knee, ' if self.bg_use_knee else '') + \
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


    def _clear_settings(self):
        """Clears all setting for current instance, setting them all to None."""

        attributes = get_attribute_names()
        for setting in attributes['all_settings']:
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
