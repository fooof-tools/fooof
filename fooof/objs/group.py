"""FOOOFGroup object and associated code for using the FOOOF model on 2D groups of power spectra.

Notes
-----
FOOOFGroup object docs are imported from FOOOF object at runtime.
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np

from fooof.objs import FOOOF
from fooof.plts.fg import plot_fg
from fooof.core.items import OBJ_DESC
from fooof.core.info import get_indices
from fooof.core.utils import check_inds
from fooof.core.errors import NoModelError
from fooof.core.reports import save_report_fg
from fooof.core.strings import gen_results_fg_str
from fooof.core.io import save_fg, load_jsonlines
from fooof.core.modutils import copy_doc_func_to_method, safe_import
from fooof.data.conversions import group_to_dataframe

###################################################################################################
###################################################################################################

class FOOOFGroup(FOOOF):
    """Model a group of power spectra as a combination of aperiodic and periodic components.

    WARNING: FOOOF expects frequency and power values in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    peak_width_limits : tuple of (float, float), optional, default: (0.5, 12.0)
        Limits on possible peak width, as (lower_bound, upper_bound).
    max_n_peaks : int, optional, default: inf
        Maximum number of gaussians to be fit in a single spectrum.
    min_peak_height : float, optional, default: 0
        Absolute threshold for detecting peaks, in units of the input data.
    peak_threshold : float, optional, default: 2.0
        Relative threshold for detecting peaks, in units of standard deviation of the input data.
    aperiodic_mode : {'fixed', 'knee'}
        Which approach to take for fitting the aperiodic component.
    verbose : bool, optional, default: True
        Verbosity mode. If True, prints out warnings and general status updates.

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the power spectra.
    power_spectra : 2d array
        Power values for the group of power spectra, as [n_power_spectra, n_freqs].
        Power values are stored internally in log10 scale.
    freq_range : list of [float, float]
        Frequency range of the power spectra, as [lowest_freq, highest_freq].
    freq_res : float
        Frequency resolution of the power spectra.
    group_results : list of FOOOFResults
        Results of FOOOF model fit for each power spectrum.
    has_data : bool
        Whether data is loaded to the object.
    has_model : bool
        Whether model results are available in the object.
    n_peaks_ : int
        The number of peaks fit in the model.
    n_failed_fits_ : int
        The number of models that failed to fit.
    failed_fit_inds_ : list of int
        The indices of any models that failed to fit.

    Notes
    -----
    - Commonly used abbreviations used in this module include:
      CF: center frequency, PW: power, BW: Bandwidth, AP: aperiodic
    - Input power spectra must be provided in linear scale.
      Internally they are stored in log10 scale, as this is what the model operates upon.
    - Input power spectra should be smooth, as overly noisy power spectra may lead to bad fits.
      For example, raw FFT inputs are not appropriate. Where possible and appropriate, use
      longer time segments for power spectrum calculation to get smoother power spectra,
      as this will give better model fits.
    - The gaussian params are those that define the gaussian of the fit, where as the peak
      params are a modified version, in which the CF of the peak is the mean of the gaussian,
      the PW of the peak is the height of the gaussian over and above the aperiodic component,
      and the BW of the peak, is 2*std of the gaussian (as 'two sided' bandwidth).
    - The FOOOFGroup object inherits from the FOOOF object. As such it also has data
      attributes (`power_spectrum` & `fooofed_spectrum_`), and parameter attributes
      (`aperiodic_params_`, `peak_params_`, `gaussian_params_`, `r_squared_`, `error_`)
      which are defined in the context of individual model fits. These attributes are
      used during the fitting process, but in the group context do not store results
      post-fitting. Rather, all model fit results are collected and stored into the
      `group_results` attribute. To access individual parameters of the fit, use
      the `get_params` method.
    """
    # pylint: disable=attribute-defined-outside-init, arguments-differ

    def __init__(self, *args, **kwargs):
        """Initialize object with desired settings."""

        FOOOF.__init__(self, *args, **kwargs)

        self.power_spectra = None

        self._reset_group_results()


    def __len__(self):
        """Define the length of the object as the number of model fit results available."""

        return len(self.group_results)


    def __iter__(self):
        """Allow for iterating across the object by stepping across model fit results."""

        for result in self.group_results:
            yield result


    def __getitem__(self, index):
        """Allow for indexing into the object to select model fit results."""

        return self.group_results[index]


    @property
    def has_data(self):
        """Indicator for if the object contains data."""

        return True if np.any(self.power_spectra) else False


    @property
    def has_model(self):
        """Indicator for if the object contains model fits."""

        return True if self.group_results else False


    @property
    def n_peaks_(self):
        """How many peaks were fit for each model."""

        return [f_res.peak_params.shape[0] for f_res in self] if self.has_model else None


    @property
    def n_null_(self):
        """How many model fits are null."""

        return sum([1 for f_res in self.group_results if np.isnan(f_res.aperiodic_params[0])]) \
            if self.has_model else None


    @property
    def null_inds_(self):
        """The indices for model fits that are null."""

        return [ind for ind, f_res in enumerate(self.group_results) \
            if np.isnan(f_res.aperiodic_params[0])] \
            if self.has_model else None


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False,
                            clear_results=False, clear_spectra=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        clear_spectra : bool, optional, default: False
            Whether to clear power spectra attribute.
        """

        super()._reset_data_results(clear_freqs, clear_spectrum, clear_results)
        if clear_spectra:
            self.power_spectra = None


    def _reset_group_results(self, length=0):
        """Set, or reset, results to be empty.

        Parameters
        ----------
        length : int, optional, default: 0
            Length of list of empty lists to initialize. If 0, creates a single empty list.
        """

        self.group_results = [[]] * length


    def add_data(self, freqs, power_spectra, freq_range=None):
        """Add data (frequencies and power spectrum values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        power_spectra : 2d array, shape=[n_power_spectra, n_freqs]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if np.any(self.freqs):
            self._reset_data_results(True, True, True, True)
            self._reset_group_results()

        self.freqs, self.power_spectra, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, power_spectra, freq_range, 2)


    def report(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1, progress=None):
        """Fit a group of power spectra and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        self.fit(freqs, power_spectra, freq_range, n_jobs=n_jobs, progress=progress)
        self.plot()
        self.print_results(False)


    def fit(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1, progress=None):
        """Fit a group of power spectra.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Desired frequency range to run FOOOF on. If not provided, fits the entire given range.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If freqs & power spectra provided together, add data to object
        if freqs is not None and power_spectra is not None:
            self.add_data(freqs, power_spectra, freq_range)

        # If 'verbose', print out a marker of what is being run
        if self.verbose and not progress:
            print('Running FOOOFGroup across {} power spectra.'.format(len(self.power_spectra)))

        # Run linearly
        if n_jobs == 1:
            self._reset_group_results(len(self.power_spectra))
            for ind, power_spectrum in \
                _progress(enumerate(self.power_spectra), progress, len(self)):
                self._fit(power_spectrum=power_spectrum)
                self.group_results[ind] = self._get_results()

        # Run in parallel
        else:
            self._reset_group_results()
            n_jobs = cpu_count() if n_jobs == -1 else n_jobs
            with Pool(processes=n_jobs) as pool:
                self.group_results = list(_progress(pool.imap(partial(_par_fit, fg=self),
                                                              self.power_spectra),
                                                    progress, len(self.power_spectra)))

        # Clear the individual power spectrum and fit results of the current fit
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    def drop(self, inds):
        """Drop one or more model fit results from the object.

        Parameters
        ----------
        inds : int or array_like of int or array_like of bool
            Indices to drop model fit results for.
            If a boolean mask, True indicates indices to drop.

        Notes
        -----
        This method sets the model fits as null, and preserves the shape of the model fits.
        """

        for ind in check_inds(inds):
            fm = self.get_fooof(ind)
            fm._reset_data_results(clear_results=True)
            self.group_results[ind] = fm.get_results()


    def get_results(self):
        """Return the results run across a group of power spectra."""

        return self.group_results


    def get_params(self, name, col=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract across the group.
        col : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
            Column name / index to extract from selected data, if requested.
            Only used for name of {'aperiodic_params', 'peak_params', 'gaussian_params'}.

        Returns
        -------
        out : ndarray
            Requested data.

        Raises
        ------
        NoModelError
            If there are no model fit results available.
        ValueError
            If the input for the `col` input is not understood.

        Notes
        -----
        When extracting peak information ('peak_params' or 'gaussian_params'), an additional column
        is appended to the returned array, indicating the index of the model that the peak came from.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")

        # Allow for shortcut alias, without adding `_params`
        if name in ['aperiodic', 'peak', 'gaussian']:
            name = name + '_params'

        # If col specified as string, get mapping back to integer
        if isinstance(col, str):
            col = get_indices(self.aperiodic_mode)[col]
        elif isinstance(col, int):
            if col not in [0, 1, 2]:
                raise ValueError("Input value for `col` not valid.")

        # Pull out the requested data field from the group data
        # As a special case, peak_params are pulled out in a way that appends
        #  an extra column, indicating which FOOOF run each peak comes from
        if name in ('peak_params', 'gaussian_params'):

            # Collect peak data, appending the index of the model it comes from
            out = np.vstack([np.insert(getattr(data, name), 3, index, axis=1)
                             for index, data in enumerate(self.group_results)])

            # This updates index to grab selected column, and the last column
            #  This last column is the 'index' column (FOOOF object source)
            if col is not None:
                col = [col, -1]
        else:
            out = np.array([getattr(data, name) for data in self.group_results])

        # Select out a specific column, if requested
        if col is not None:
            out = out[:, col]

        return out


    @copy_doc_func_to_method(plot_fg)
    def plot(self, save_fig=False, file_name=None, file_path=None, **plot_kwargs):

        plot_fg(self, save_fig=save_fig, file_name=file_name, file_path=file_path, **plot_kwargs)


    @copy_doc_func_to_method(save_report_fg)
    def save_report(self, file_name, file_path=None, add_settings=True):

        save_report_fg(self, file_name, file_path, add_settings)


    @copy_doc_func_to_method(save_fg)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_fg(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None):
        """Load FOOOFGroup data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_group_results()

        power_spectra = []
        for ind, data in enumerate(load_jsonlines(file_name, file_path)):

            self._add_from_dict(data)

            # If settings are loaded, check and update based on the first line
            if ind == 0:
                self._check_loaded_settings(data)

            # If power spectra data is part of loaded data, collect to add to object
            if 'power_spectrum' in data.keys():
                power_spectra.append(data['power_spectrum'])

            # If results part of current data added, check and update object results
            if set(OBJ_DESC['results']).issubset(set(data.keys())):
                self._check_loaded_results(data)
                self.group_results.append(self._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.freq_range:
            self._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.power_spectra = np.array(power_spectra)

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    def get_fooof(self, ind, regenerate=True):
        """Get a FOOOF object for a specified model fit.

        Parameters
        ----------
        ind : int
            The index of the FOOOFResults in FOOOFGroup.group_results to load.
        regenerate : bool, optional, default: False
            Whether to regenerate the model fits from the given fit parameters.

        Returns
        -------
        fm : FOOOF
            The FOOOFResults data loaded into a FOOOF object.
        """

        # Initialize a FOOOF object, with same settings & check data mode as current FOOOFGroup
        fm = FOOOF(*self.get_settings(), verbose=self.verbose)
        fm.set_check_data_mode(self._check_data)

        # Add data for specified single power spectrum, if available
        #   The power spectrum is inverted back to linear, as it is re-logged when added to FOOOF
        if self.has_data:
            fm.add_data(self.freqs, np.power(10, self.power_spectra[ind]))
        # If no power spectrum data available, copy over data information & regenerate freqs
        else:
            fm.add_meta_data(self.get_meta_data())

        # Add results for specified power spectrum, regenerating full fit if requested
        fm.add_results(self.group_results[ind])
        if regenerate:
            fm._regenerate_model()

        return fm


    def get_group(self, inds):
        """Get a FOOOFGroup object with the specified sub-selection of model fits.

        Parameters
        ----------
        inds : array_like of int or array_like of bool
            Indices to extract from the object.
            If a boolean mask, True indicates indices to select.

        Returns
        -------
        fg : FOOOFGroup
            The requested selection of results data loaded into a new FOOOFGroup object.
        """

        # Check and convert indices encoding to list of int
        inds = check_inds(inds)

        # Initialize a new FOOOFGroup object, with same settings as current FOOOFGroup
        fg = FOOOFGroup(*self.get_settings(), verbose=self.verbose)

        # Add data for specified power spectra, if available
        #   The power spectra are inverted back to linear, as they are re-logged when added to FOOOF
        if self.has_data:
            fg.add_data(self.freqs, np.power(10, self.power_spectra[inds, :]))
        # If no power spectrum data available, copy over data information & regenerate freqs
        else:
            fg.add_meta_data(self.get_meta_data())

        # Add results for specified power spectra
        fg.group_results = [self.group_results[ind] for ind in inds]

        return fg


    def print_results(self, concise=False):
        """Print out FOOOFGroup results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_results_fg_str(self, concise))


    def save_model_report(self, index, file_name, file_path=None, plt_log=False,
                          add_settings=True, **plot_kwargs):
        """"Save out an individual model report for a specified model fit.

        Parameters
        ----------
        index : int
            Index of the model fit to save out.
        file_name : str
            Name to give the saved out file.
        file_path : str, optional
            Path to directory to save to. If None, saves to current directory.
        plt_log : bool, optional, default: False
            Whether or not to plot the frequency axis in log space.
        add_settings : bool, optional, default: True
            Whether to add a print out of the model settings to the end of the report.
        plot_kwargs : keyword arguments
            Keyword arguments to pass into the plot method.
        """

        self.get_fooof(ind=index, regenerate=True).save_report(\
            file_name, file_path, plt_log, **plot_kwargs)


    def to_df(self, peak_org):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.

        Returns
        -------
        pd.DataFrame
            Model results organized into a pandas object.
        """

        return group_to_dataframe(self.get_results(), peak_org)


    def _fit(self, *args, **kwargs):
        """Create an alias to FOOOF.fit for FOOOFGroup object, for internal use."""

        super().fit(*args, **kwargs)


    def _get_results(self):
        """Create an alias to FOOOF.get_results for FOOOFGroup object, for internal use."""

        return super().get_results()

    def _check_width_limits(self):
        """Check and warn about bandwidth limits / frequency resolution interaction."""

        # Only check & warn on first power spectrum
        #   This is to avoid spamming standard output for every spectrum in the group
        if self.power_spectra[0, 0] == self.power_spectrum[0]:
            super()._check_width_limits()

###################################################################################################
###################################################################################################

def _par_fit(power_spectrum, fg):
    """Helper function for running in parallel."""

    fg._fit(power_spectrum=power_spectrum)

    return fg._get_results()


def _progress(iterable, progress, n_to_run):
    """Add a progress bar to an iterable to be processed.

    Parameters
    ----------
    iterable : list or iterable
        Iterable object to potentially apply progress tracking to.
    progress : {None, 'tqdm', 'tqdm.notebook'}
        Which kind of progress bar to use. If None, no progress bar is used.
    n_to_run : int
        Number of jobs to complete.

    Returns
    -------
    pbar : iterable or tqdm object
        Iterable object, with tqdm progress functionality, if requested.

    Raises
    ------
    ValueError
        If the input for `progress` is not understood.

    Notes
    -----
    The explicit `n_to_run` input is required as tqdm requires this in the parallel case.
    The `tqdm` object that is potentially returned acts the same as the underlying iterable,
    with the addition of printing out progress every time items are requested.
    """

    # Check progress specifier is okay
    tqdm_options = ['tqdm', 'tqdm.notebook']
    if progress is not None and progress not in tqdm_options:
        raise ValueError("Progress bar option not understood.")

    # Set the display text for the progress bar
    pbar_desc = 'Running FOOOFGroup'

    # Use a tqdm, progress bar, if requested
    if progress:

        # Try loading the tqdm module
        tqdm = safe_import(progress)

        if not tqdm:

            # If tqdm isn't available, proceed without a progress bar
            print(("A progress bar requiring the 'tqdm' module was requested, "
                   "but 'tqdm' is not installed. \nProceeding without using a progress bar."))
            pbar = iterable

        else:

            # If tqdm loaded, apply the progress bar to the iterable
            pbar = tqdm.tqdm(iterable, desc=pbar_desc, total=n_to_run, dynamic_ncols=True)

    # If progress is None, return the original iterable without a progress bar applied
    else:
        pbar = iterable

    return pbar
