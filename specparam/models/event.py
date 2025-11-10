"""Event model object and associated code for fitting the model to spectrograms across events."""

import numpy as np

from specparam.models import SpectralModel, SpectralTimeModel
from specparam.results.results import Results3D
from specparam.results.utils import run_parallel_event, pbar
from specparam.data.data import Data3D
from specparam.data.conversions import event_group_to_dataframe, dict_to_df
from specparam.data.utils import flatten_results_dict
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.reports.save import save_event_report
from specparam.reports.strings import gen_event_results_str
from specparam.plts.event import plot_event_model
from specparam.io.utils import get_files
from specparam.io.models import save_event
from specparam.utils.checks import check_inds

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Attributes'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralTimeEventModel(SpectralTimeModel):
    """Model a set of event as a combination of aperiodic and periodic components.

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
    - The event object inherits from the time model, overwriting the `data` and
      `results` objects with versions for fitting models across events.
      Event related, temporally organized results are collected into the
      `results.event_time_results` attribute, which may include sub-selecting peaks
      per band (depending on settings). Note that the `results.event_group_results` attribute
      is also available, which maintains the full model results.
    """

    def __init__(self, *args, **kwargs):
        """Initialize event model object."""

        SpectralTimeModel.__init__(self, *args,
                                   aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                                   periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                                   verbose=kwargs.pop('verbose', True),
                                   **kwargs)

        self.data = Data3D()

        self.results = Results3D(modes=self.modes,
                                 metrics=kwargs.pop('metrics', None),
                                 bands=kwargs.pop('bands', None))

        self.algorithm._reset_subobjects(data=self.data, results=self.results)


    def add_data(self, freqs, spectrograms, freq_range=None, clear_results=True):
        """Add data (frequencies and spectrograms) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        spectrograms : 3d array or list of 2d array
            Matrix of power values, in linear space.
            If list of 2d arrays, each should be have the same shape of [n_freqs, n_time_windows].
            If 3d array, should have shape [n_events, n_freqs, n_time_windows].
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results these will be cleared
        by this method call, unless explicitly set not to.
        """

        if clear_results:
            self.results._reset_event_results()

        self.data.add_data(freqs, spectrograms, freq_range=freq_range)


    def fit(self, freqs=None, spectrograms=None, freq_range=None, bands=None,
            n_jobs=1, progress=None, prechecks=True, convert_results=True):
        """Fit a set of events.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        spectrograms : 3d array or list of 2d array
            Matrix of power values, in linear space.
            If list of 2d arrays, each should be have the same shape of [n_freqs, n_time_windows].
            If 3d array, should have shape [n_events, n_freqs, n_time_windows].
        freq_range : list of [float, float], optional
            Frequency range to fit the model to. If not provided, fits the entire given range.
        bands : Bands or dict or int, optional
            How to organize peaks into bands.
            If Bands or dict, uses band definitions. If int, extracts the first 'n' peaks.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.
        prechecks : bool, optional, default: True
            Whether to run model fitting pre-checks.
        convert_results : bool, optional, default: True
            Whether to convert results per spectrogram window to be organized over time.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        if spectrograms is not None:
            self.add_data(freqs, spectrograms, freq_range)

        if prechecks:
            self.algorithm._fit_prechecks(self.verbose)

        # If 'verbose', print out a marker of what is being run
        if self.verbose and not progress:
            print('Fitting model across {} events of {} windows.'.format(\
                len(self.data.spectrograms), self.data.n_time_windows))

        if n_jobs == 1:
            self.results._reset_event_results(len(self.data.spectrograms))
            for ind, spectrogram in \
                pbar(enumerate(self.data.spectrograms), progress, len(self.results)):
                self.data.power_spectra = spectrogram.T
                super().fit(prechecks=False, convert_results=False)
                self.results.event_group_results[ind] = self.results.group_results
                self.results._reset_group_results()
                self._reset_data_results(clear_spectra=True)

        else:
            fg = self.get_group(None, None, 'group')
            self.results.event_group_results = run_parallel_event(\
                fg, self.data.spectrograms, n_jobs, progress)

        if convert_results:
            self.convert_results(bands)


    def report(self, freqs=None, spectrograms=None, freq_range=None,
               bands=None, n_jobs=1, progress=None):
        """Fit a set of events and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        spectrograms : 3d array or list of 2d array
            Matrix of power values, in linear space.
            If a list of 2d arrays, each should be have the same shape of [n_freqs, n_time_windows].
            If a 3d array, should have shape [n_events, n_freqs, n_time_windows].
        freq_range : list of [float, float], optional
            Frequency range to fit the model to. If not provided, fits the entire given range.
        bands : Bands or dict or int, optional
            How to organize peaks into bands.
            If Bands or dict, uses band definitions. If int, extracts the first 'n' peaks.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        self.fit(freqs, spectrograms, freq_range, bands, n_jobs, progress)
        self.plot()
        self.print_results()


    def print_results(self, concise=False):
        """Print out SpectralTimeEventModel results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_event_results_str(self, concise))


    @copy_doc_func_to_method(plot_event_model)
    def plot(self, save_fig=False, file_name=None, file_path=None, **plot_kwargs):

        plot_event_model(self, save_fig=save_fig, file_name=file_name,
                         file_path=file_path, **plot_kwargs)


    @copy_doc_func_to_method(save_event_report)
    def save_report(self, file_name, file_path=None, add_settings=True):

        save_event_report(self, file_name, file_path, add_settings)


    @copy_doc_func_to_method(save_event)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_event(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None, convert_results=True):
        """Load data from file(s).

        Parameters
        ----------
        file_name : str
            File(s) to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        convert_results : bool, optional, default: True
            Whether to convert results to be organized over time.
        """

        files = get_files(file_path, select=file_name)
        spectrograms = []
        for file in files:
            super().load(file, file_path, convert_results=False)
            if self.results.group_results:
                self.results.add_results(self.results.group_results, append=True)
            if np.all(self.data.power_spectra):
                spectrograms.append(self.data.spectrogram)
        self.data.spectrograms = np.array(spectrograms) if spectrograms else None

        self.results._reset_group_results()
        if convert_results and self.results.bands and self.results.event_group_results:
            self.results.convert_results()


    def get_model(self, event_ind=None, window_ind=None, regenerate=True):
        """Get a model fit object for a specified index.

        Parameters
        ----------
        event_ind : int, optional
            Index for which event to extract from.
        window_ind : int, optional
            Index for which time window to extract from.
        regenerate : bool, optional, default: False
            Whether to regenerate the model fits for the requested model.

        Returns
        -------
        model : SpectralModel
            The data and fit results loaded into a model object.
        """

        # Initialize model object, with same settings, metadata, & check states as current object
        model = super().get_model()

        # Add data for specified single power spectrum, if available
        if event_ind is not None and window_ind is not None and self.data.has_data:
            model.data.power_spectrum = self.data.spectrograms[event_ind][:, window_ind]

        # Add results for specified power spectrum, regenerating full fit if requested
        if event_ind is not None and window_ind is not None:
            model.results.add_results(self.results.event_group_results[event_ind][window_ind])
            if regenerate:
                model.results._regenerate_model(self.data.freqs)

        return model


    def get_group(self, event_inds, window_inds, output_type='event'):
        """Get a new model object with the specified sub-selection of model fits.

        Parameters
        ----------
        event_inds, window_inds : array_like of int or array_like of bool or None
            Indices to extract from the object, for event and time windows.
            If None, selects all available indices.
        output_type : {'time', 'group'}, optional
            Type of model object to extract:
                'event' : SpectralTimeEventObject
                'time' : SpectralTimeObject
                'group' : SpectralGroupObject

        Returns
        -------
        output : SpectralTimeEventModel
            The requested selection of results data loaded into a new model object.
        """

        # Check and convert indices encoding to list of int
        einds = check_inds(event_inds, self.data.n_events)
        winds = check_inds(window_inds, self.data.n_time_windows)

        if output_type == 'event':

            # Local import - avoid circularity
            from specparam.models.utils import initialize_model_from_source

            # Initialize a new model object, with same settings as current object
            output = initialize_model_from_source(self, 'event')

            if event_inds is not None or window_inds is not None:

                # Add data for specified power spectra, if available
                if self.data.has_data:
                    output.data.spectrograms = self.data.spectrograms[einds, :, :][:, :, winds]

                # Add results for specified power spectra - event group results
                temp = [self.results.event_group_results[ei][wi] for ei in einds for wi in winds]
                step = int(len(temp) / len(einds))
                output.results.event_group_results = \
                    [temp[ind:ind+step] for ind in range(0, len(temp), step)]

                # Add results for specified power spectra - event time results
                output.results.event_time_results = \
                    {key : self.results.event_time_results[key][event_inds][:, window_inds] \
                    for key in self.results.event_time_results}

        elif output_type in ['time', 'group']:

            if event_inds is not None or window_inds is not None:

                # Move specified results & data to `group_results` & `power_spectra` for export
                self.results.group_results = \
                    [self.results.event_group_results[ei][wi] for ei in einds for wi in winds]
                if self.data.has_data:
                    self.data.power_spectra = \
                        np.hstack(self.data.spectrograms[einds, :, :][:, :, winds]).T

            new_inds = range(0, len(self.results.group_results)) if \
                self.results.group_results else None
            output = super().get_group(new_inds, output_type)

            # Clear the data that was moved for export
            self.results._reset_group_results()
            self._reset_data_results(clear_spectra=True)

        return output


    def save_model_report(self, event_index, window_index, file_name,
                          file_path=None, add_settings=True, **plot_kwargs):
        """"Save out an individual model report for a specified model fit.

        Parameters
        ----------
        event_ind : int
            Index for which event to extract from.
        window_ind : int
            Index for which time window to extract from.
        file_name : str
            Name to give the saved out file.
        file_path : str, optional
            Path to directory to save to. If None, saves to current directory.
        add_settings : bool, optional, default: True
            Whether to add a print out of the model settings to the end of the report.
        plot_kwargs : keyword arguments
            Keyword arguments to pass into the plot method.
        """

        self.get_model(event_index, window_index, regenerate=True).save_report(\
            file_name, file_path, add_settings, **plot_kwargs)


    def to_df(self, bands=None):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        bands : Bands or dict or int, optional
            How to organize peaks into bands.
            If Bands or dict, uses band definitions. If int, extracts the first 'n' peaks.
            If provided, re-extracts peak features; if not, converts from `event_group_results`.

        Returns
        -------
        pd.DataFrame
            Model results organized into a pandas object.
        """

        if bands is not None:
            df = event_group_to_dataframe(self.results.event_group_results, self.modes, bands)
        else:
            df = dict_to_df(flatten_results_dict(self.results.get_results()))

        return df


    def convert_results(self, bands=None):
        """Convert results to be organized across time & events.

        Parameters
        ----------
        bands : Bands or dict or int, optional
            How to organize peaks into bands.
            If Bands or dict, uses band definitions. If int, extracts the first 'n' peaks.
            If not provided, uses band definition available in object.
        """

        if bands:
            self.results.add_bands(bands)
        self.results.convert_results()


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False, clear_results=False,
                            clear_spectra=False, clear_spectrograms=False):
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
        clear_spectrograms : bool, optional, default: False
            Whether to clear spectrograms attribute.
        """

        self.data._reset_data(clear_freqs, clear_spectrum, clear_spectra, clear_spectrograms)
        self.results._reset_results(clear_results)
