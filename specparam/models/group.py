"""Group model object and associated code for fitting the model to 2D groups of power spectra.

Notes
-----
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

import numpy as np

from specparam.models import SpectralModel
from specparam.data.data import Data2D
from specparam.data.conversions import group_to_dataframe
from specparam.results.results import Results2D
from specparam.results.utils import run_parallel_group, pbar
from specparam.plts.group import plot_group_model
from specparam.io.models import save_group
from specparam.io.files import load_jsonlines
from specparam.reports.save import save_group_report
from specparam.reports.strings import gen_group_results_str
from specparam.modutils.docs import (copy_doc_func_to_method,
                                     docs_get_section, replace_docstring_sections)
from specparam.utils.checks import check_inds

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Attributes'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralGroupModel(SpectralModel):

    """Model a group of power spectra as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space. Passing in logged
    frequencies and/or power spectra is not detected, and will silently produce incorrect results.

    Parameters
    ----------
    % copied in from SpectralModel object

    Attributes
    ----------
    % copied in from SpectralModel object

    Notes
    -----
    % copied in from SpectralModel object
    - The group object inherits from the model object, and in doing so overwrites the
      `data` and `results` objects with versions for fitting groups of power spectra.
      All model fit results are collected and stored in the `results.group_results` attribute.
      To access individual parameters of the fit, use the `get_params` method.
    """

    def __init__(self, *args, **kwargs):
        """Initialize group model object."""

        SpectralModel.__init__(self, *args,
                               aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                               periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                               verbose=kwargs.pop('verbose', True),
                               **kwargs)

        self.data = Data2D()

        self.results = Results2D(modes=self.modes,
                                 metrics=kwargs.pop('metrics', None),
                                 bands=kwargs.pop('bands', None))

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


    def fit(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1,
            progress=None, prechecks=True):
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
        prechecks : bool, optional, default: True
            Whether to run model fitting pre-checks.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If freqs & power spectra provided together, add data to object
        if freqs is not None and power_spectra is not None:
            self.add_data(freqs, power_spectra, freq_range)

        # Run pre-checks
        if prechecks:
            self.algorithm._fit_prechecks(self.verbose)

        # If 'verbose', print out a marker of what is being run
        if self.verbose and not progress:
            print('Fitting model across {} power spectra.'.format(len(self.data.power_spectra)))

        # Run linearly
        if n_jobs == 1:
            self.results._reset_group_results(len(self.data.power_spectra))
            for ind, power_spectrum in \
                pbar(enumerate(self.data.power_spectra), progress, len(self.results)):
                self._pass_through_spectrum(power_spectrum)
                super().fit(prechecks=False)
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

            data_keys = set(data.keys())
            self._add_from_dict(data)

            # For hearder line, check if settings are loaded and clear defaults if not
            if ind == 0 and not set(self.algorithm.settings.names).issubset(data_keys):
                self.algorithm.settings.clear()

            # If results part of current data added, check and update object results
            if 'aperiodic_fit' in data_keys:
                self.results.group_results.append(self.results._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.data.freq_range:
            self.data._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.data.power_spectra = np.array(power_spectra)

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    @copy_doc_func_to_method(Results2D.get_params)
    def get_params(self, component, field=None):

        return self.results.get_params(component, field)


    @copy_doc_func_to_method(Results2D.get_metrics)
    def get_metrics(self, category, measure=None):

        return self.results.get_metrics(category, measure)


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
        if ind is not None:
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


    def to_df(self, bands=None):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        bands : Bands or int, optional
            How to organize peaks into bands.
            If Bands, extracts peaks based on band definitions.
            If int, extracts the first n peaks.
            If not provided, uses the bands definition available in the object.

        Returns
        -------
        pd.DataFrame
            Model results organized into a pandas object.
        """

        if not bands:
            bands = self.results.bands

        return group_to_dataframe(self.results.get_results(), self.modes, bands)


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
