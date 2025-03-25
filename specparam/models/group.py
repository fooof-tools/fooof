"""Group model object and associated code for fitting the model to 2D groups of power spectra.

Notes
-----
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

import numpy as np

from specparam.models import SpectralModel
from specparam.objs.data import BaseData2D
from specparam.objs.results import BaseResults2D
from specparam.objs.utils import run_parallel_group, pbar
from specparam.plts.group import plot_group_model
from specparam.io.models import save_group
from specparam.io.files import load_jsonlines
from specparam.reports.save import save_group_report
from specparam.reports.strings import gen_group_results_str
from specparam.modutils.docs import (copy_doc_func_to_method,
                                     docs_get_section, replace_docstring_sections)
from specparam.data.conversions import group_to_dataframe
from specparam.utils.checks import check_inds

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralGroupModel(SpectralModel):

    """Model a group of power spectra as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    % copied in from SpectralModel object

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
    group_results : list of FitResults
        Results of the model fit for each power spectrum.
    has_data : bool
        Whether data is loaded to the object.
    has_model : bool
        Whether model results are available in the object.
    n_peaks_ : int
        The number of peaks fit in the model.
    n_null_ : int
        The number of models that failed to fit and/or that are marked as null.
    null_inds_ : list of int
        The indices of any models that are null.

    Notes
    -----
    % copied in from SpectralModel object
    - The group object inherits from the model object. As such it also has data
      attributes (`power_spectrum` & `modeled_spectrum_`), and parameter attributes
      (`aperiodic_params_`, `peak_params_`, `gaussian_params_`, `r_squared_`, `error_`)
      which are defined in the context of individual model fits. These attributes are
      used during the fitting process, but in the group context do not store results
      post-fitting. Rather, all model fit results are collected and stored into the
      `group_results` attribute. To access individual parameters of the fit, use
      the `get_params` method.
    """

    def __init__(self, *args, **kwargs):
        """Initialize group model object."""

        SpectralModel.__init__(self, *args,
                               aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                               periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                               verbose=kwargs.pop('verbose', True),
                               **kwargs)

        self.data = BaseData2D()
        self.results = BaseResults2D(modes=self.modes)
        self.algorithm._reset_subobjects(data=self.data, results=self.results)


    def add_data(self, freqs, power_spectra, freq_range=None, clear_results=True):
        """Add data (frequencies and power spectrum values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        power_spectra : 2d array, shape=[n_power_spectra, n_freqs]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if clear_results and self.data.has_data:
            self._reset_data_results(True, True, True, True)
            self.results._reset_group_results()

        self.data.add_data(freqs, power_spectra, freq_range=freq_range)


    def fit(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1, progress=None):
        """Fit a group of power spectra.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to fit the model to. If not provided, fits the entire given range.
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
            print('Fitting model across {} power spectra.'.format(len(self.data.power_spectra)))

        # Run linearly
        if n_jobs == 1:
            self.results._reset_group_results(len(self.data.power_spectra))
            for ind, power_spectrum in \
                pbar(enumerate(self.data.power_spectra), progress, len(self.results)):
                self._pass_through_spectrum(power_spectrum)
                super().fit()
                self.results.group_results[ind] = self.results._get_results()

        # Run in parallel
        else:
            self.results._reset_group_results()
            self.results.group_results = run_parallel_group(\
                self, self.data.power_spectra, n_jobs, progress)

        # Clear the individual power spectrum and fit results of the current fit
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    def report(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1,
               progress=None, **plot_kwargs):
        """Fit a group of power spectra and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_power_spectra, n_freqs], optional
            Matrix of power spectrum values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to fit the model to. If not provided, fits the entire given range.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.
        **plot_kwargs
            Keyword arguments to pass into the plot method.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        self.fit(freqs, power_spectra, freq_range, n_jobs=n_jobs, progress=progress)
        self.plot(**plot_kwargs)
        self.print_results(False)


    @copy_doc_func_to_method(plot_group_model)
    def plot(self, **plot_kwargs):

        plot_group_model(self, **plot_kwargs)


    @copy_doc_func_to_method(save_group)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_group(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None):
        """Load group data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : Path or str, optional
            Path to directory to load from. If None, loads from current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self.results._reset_group_results()

        power_spectra = []
        for ind, data in enumerate(load_jsonlines(file_name, file_path)):

            # If power spectra data is part of loaded data, collect to add to object
            if 'power_spectrum' in data.keys():
                power_spectra.append(data.pop('power_spectrum'))

            self._add_from_dict(data)

            # If settings are loaded, check and update based on the first line
            if ind == 0:
                self._check_loaded_modes(data)
                self.algorithm._check_loaded_settings(data)

            # If results part of current data added, check and update object results
            if set(self.results._fields).issubset(set(data.keys())):
                self.results._check_loaded_results(data)
                self.results.group_results.append(self.results._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.data.freq_range:
            self.data._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.data.power_spectra = np.array(power_spectra)

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    def get_model(self, ind=None, regenerate=True):
        """Get a model fit object for a specified index.

        Parameters
        ----------
        ind : int, optional
            The index of the model from `group_results` to access.
            If None, return a Model object with initialized settings, with no data or results.
        regenerate : bool, optional, default: False
            Whether to regenerate the model fits for the requested model.

        Returns
        -------
        model : SpectralModel
            The data and fit results loaded into a model object.
        """

        # Local import - avoid circularity
        from specparam.models.utils import initialize_model_from_source

        # Initialize model object, with same settings, metadata, & check mode as current object
        model = initialize_model_from_source(self, 'model')

        # Add data for specified single power spectrum, if available
        if ind is not None and self.data.has_data:
            model.data.power_spectrum = self.data.power_spectra[ind]

        # Add results for specified power spectrum, regenerating full fit if requested
        if ind:
            model.results.add_results(self.results.group_results[ind])
            if regenerate:
                model.results._regenerate_model(self.data.freqs)

        return model


    def get_group(self, inds):
        """Get a Group model object with the specified sub-selection of model fits.

        Parameters
        ----------
        inds : array_like of int or array_like of bool
            Indices to extract from the object.

        Returns
        -------
        group : SpectralGroupModel
            The requested selection of results data loaded into a new group model object.
        """

        # Local import - avoid circularity
        from specparam.models.utils import initialize_model_from_source

        # Initialize a new model object, with same settings as current object
        group = initialize_model_from_source(self, 'group')

        if inds is not None:

            # Check and convert indices encoding to list of int
            inds = check_inds(inds)

            # Add data for specified power spectra, if available
            if self.data.has_data:
                group.data.power_spectra = self.data.power_spectra[inds, :]

            # Add results for specified power spectra
            group.results.group_results = [self.results.group_results[ind] for ind in inds]

        return group


    @copy_doc_func_to_method(save_group_report)
    def save_report(self, file_name, file_path=None, add_settings=True):

        save_group_report(self, file_name, file_path, add_settings)


    def print_results(self, concise=False):
        """Print out the group results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_group_results_str(self, concise))


    def save_model_report(self, index, file_name, file_path=None,
                          add_settings=True, **plot_kwargs):
        """"Save out an individual model report for a specified model fit.

        Parameters
        ----------
        index : int
            Index of the model fit to save out.
        file_name : str
            Name to give the saved out file.
        file_path : Path or str, optional
            Path to directory to save to. If None, saves to current directory.
        add_settings : bool, optional, default: True
            Whether to add a print out of the model settings to the end of the report.
        plot_kwargs : keyword arguments
            Keyword arguments to pass into the plot method.
        """

        self.get_model(ind=index, regenerate=True).save_report(\
            file_name, file_path, add_settings, **plot_kwargs)


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

        return group_to_dataframe(self.results.get_results(), peak_org)


    def _fit_prechecks(self):
        """Overloads fit prechecks.

        Notes
        -----
        This overloads fit prechecks to only run once (on the first spectrum), to avoid
        checking and reporting on every spectrum and repeatedly re-raising the same warning.
        """

        if self.data.power_spectra[0, 0] == self.data.power_spectrum[0]:
            super()._fit_prechecks()


    def _pass_through_spectrum(self, power_spectrum):
        """Pass through a power spectrum to add to object.

        Notes
        -----
        Passing through a spectrum like this assumes there is an existing & consistent frequency
        definition to use and that the power_spectrum is already logged, with correct freq_range.
        This should only be done internally for passing through individual spectra that
        have already undergone data checking during data adding.
        """

        self.data.power_spectrum = power_spectrum


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

        self.data._reset_data(clear_freqs, clear_spectrum, clear_spectra)
        self.results._reset_results(clear_results)
