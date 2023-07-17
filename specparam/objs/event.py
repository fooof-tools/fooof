"""Event model object and associated code for fitting the model to spectrograms across events."""

from itertools import repeat
from functools import partial
from multiprocessing import Pool, cpu_count

import numpy as np

from specparam.objs import SpectralModel, SpectralGroupModel, SpectralTimeModel
from specparam.plts.event import plot_event_model
from specparam.data.conversions import event_group_to_dict, event_group_to_dataframe, dict_to_df
from specparam.data.utils import get_group_params, get_results_by_row, flatten_results_dict
from specparam.core.modutils import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.core.reports import save_event_report
from specparam.core.strings import gen_event_results_str
from specparam.core.utils import check_inds
from specparam.core.io import get_files, save_group

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralTimeEventModel(SpectralTimeModel):
    """Model a set of event as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    %copied in from SpectralModel object

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the power spectra.
    spectrograms : 3d array
        Power values for the spectrograms, organized as [n_events, n_freqs, n_time_windows].
        Power values are stored internally in log10 scale.
    freq_range : list of [float, float]
        Frequency range of the power spectra, as [lowest_freq, highest_freq].
    freq_res : float
        Frequency resolution of the power spectra.
    event_group_results : list of list of FitResults
        Full model results collected across all events and models.
    event_time_results : dict
        Results of the model fit across each time window, collected across events.
        Each value in the dictionary stores a model fit parameter, as [n_events, n_time_windows].

    Notes
    -----
    %copied in from SpectralModel object
    - The event object inherits from the time model, which in turn inherits from the
      group object, etc. As such it also has data attributes defined on the underlying
      objects (see notes and attribute lists in inherited objects for details).
    """

    def __init__(self, *args, **kwargs):
        """Initialize object with desired settings."""

        SpectralTimeModel.__init__(self, *args, **kwargs)

        self.spectrograms = None

        self._reset_event_results()


    def __len__(self):
        """Redefine the length of the objects as the number of event results."""

        return len(self.event_group_results)


    def __getitem__(self, ind):
        """Allow for indexing into the object to select fit results for a specific event."""

        return get_results_by_row(self.event_time_results, ind)


    def _reset_event_results(self, length=0):
        """Set, or reset, event results to be empty."""

        self.event_group_results = [[]] * length
        self.event_time_results = {}


    @property
    def has_data(self):
        """Redefine has_data marker to reflect the spectrograms attribute."""

        return True if np.any(self.spectrograms) else False


    @property
    def has_model(self):
        """Redefine has_model marker to reflect the event results."""

        return True if self.event_group_results else False


    @property
    def n_peaks_(self):
        """How many peaks were fit for each model, for each event."""

        return np.array([[res.peak_params.shape[0] for res in gres] \
            if self.has_model else None for gres in self.event_group_results])


    @property
    def n_events(self):
        # ToDo: double check if we want this - I think is never used internally?

        return len(self)


    @property
    def n_time_windows(self):
        # ToDo: double check if we want this - I think is never used internally?

        return self.spectrograms[0].shape[1] if self.has_data else 0


    def add_data(self, freqs, spectrograms, freq_range=None):
        """Add data (frequencies and spectrograms) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        spectrograms : 3d array or list of 2d array
            Matrix of power values, in linear space.
            If a list of 2d arrays, each should be have the same shape of [n_freqs, n_time_windows].
            If a 3d array, should have shape [n_events, n_freqs, n_time_windows].
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If given a list of spectrograms, convert to 3d array
        if isinstance(spectrograms, list):
            spectrograms = np.array(spectrograms)

        # If is a 3d array, add to object as spectrograms
        if spectrograms.ndim == 3:

            if np.any(self.freqs):
                self._reset_event_results()

            self.freqs, self.spectrograms, self.freq_range, self.freq_res = \
                self._prepare_data(freqs, spectrograms, freq_range, 3)

        # Otherwise, pass through 2d array to underlying object method
        else:
            super().add_data(freqs, spectrograms, freq_range)


    def report(self, freqs=None, spectrograms=None, freq_range=None,
               peak_org=None, n_jobs=1, progress=None):
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
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        self.fit(freqs, spectrograms, freq_range, peak_org, n_jobs=n_jobs, progress=progress)
        self.plot()
        self.print_results()


    def fit(self, freqs=None, spectrograms=None, freq_range=None, peak_org=None,
            n_jobs=1, progress=None):
        """Fit a set of events.

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
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        n_jobs : int, optional, default: 1
            Number of jobs to run in parallel.
            1 is no parallelization. -1 uses all available cores.
        progress : {None, 'tqdm', 'tqdm.notebook'}, optional
            Which kind of progress bar to use. If None, no progress bar is used.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # ToDo: here because of circular import - updates / refactors should fix & move
        from specparam.objs.group import _progress

        if spectrograms is not None:
            self.add_data(freqs, spectrograms, freq_range)

        if n_jobs == 1:
            self._reset_event_results(len(self.spectrograms))
            for ind, spectrogram in _progress(enumerate(self.spectrograms), progress, len(self)):
                self.power_spectra = spectrogram.T
                super().fit(peak_org=False)
                self.event_group_results[ind] = self.group_results
                self._reset_group_results()
                self._reset_data_results(clear_spectra=True)

        else:

            ft = SpectralGroupModel(*self.get_settings(), verbose=False)
            ft.add_meta_data(self.get_meta_data())
            ft.freqs = self.freqs

            n_jobs = cpu_count() if n_jobs == -1 else n_jobs
            with Pool(processes=n_jobs) as pool:

                self.event_group_results = \
                    list(_progress(pool.imap(partial(_par_fit, model=ft), self.spectrograms),
                                   progress, len(self.spectrograms)))

        if peak_org is not False:
            self.convert_results(peak_org)


    def drop(self, drop_inds=None, window_inds=None):
        """Drop one or more model fit results from the object.

        Parameters
        ----------
        drop_inds : dict or int or array_like of int or array_like of bool
            Indices to drop model fit results for.
            If not dict, specifies the event indices, with time windows specified by `window_inds`.
            If dict, each key reflects an event index, with corresponding time windows to drop.
        window_inds : int or array_like of int or array_like of bool
            Indices of time windows to drop model fits for (applied across all events).
            Only used if `drop_inds` is not a dictionary.

        Notes
        -----
        This method sets the model fits as null, and preserves the shape of the model fits.
        """

        null_model = SpectralModel(*self.get_settings()).get_results()

        drop_inds = drop_inds if isinstance(drop_inds, dict) else \
            {eind : winds for eind, winds in zip(check_inds(drop_inds), repeat(window_inds))}

        for eind, winds in drop_inds.items():

            winds = check_inds(winds)
            for wind in winds:
                self.event_group_results[eind][wind] = null_model
            for key in self.event_time_results:
                self.event_time_results[key][eind, winds] = np.nan


    def get_results(self):
        """Return the results from across the set of events."""

        return self.event_time_results


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
        out : list of ndarray
            Requested data.

        Raises
        ------
        NoModelError
            If there are no model fit results available.
        ValueError
            If the input for the `col` input is not understood.

        Notes
        -----
        When extracting peak information ('peak_params' or 'gaussian_params'), an additional
        column is appended to the returned array, indicating the index that the peak came from.
        """

        return [get_group_params(gres, name, col) for gres in self.event_group_results]


    def get_group(self, event_inds, window_inds):
        """Get a new model object with the specified sub-selection of model fits.

        Parameters
        ----------
        event_inds, window_inds : array_like of int or array_like of bool
            Indices to extract from the object, for event and time windows.

        Returns
        -------
        output : SpectralTimeEventModel
            The requested selection of results data loaded into a new model object.
        """

        # Initialize a new model object, with same settings as current object
        output = SpectralTimeEventModel(*self.get_settings(), verbose=self.verbose)
        output.add_meta_data(self.get_meta_data())

        if event_inds is not None or window_inds is not None:

            # Check and convert indices encoding to list of int
            event_inds = check_inds(event_inds)
            window_inds = check_inds(window_inds)

            # Add data for specified power spectra, if available
            if self.has_data:
                output.spectrograms = self.spectrograms[event_inds, :, :][:, :, window_inds]

            # Add results for specified power spectra
            # ToDo: this doesn't work... needs fixing.
            # output.event_group_results = \
            #     [self.event_group_results[eind][wind] for eind in event_inds for wind in window_inds]
            output.event_time_results = \
                {key : self.event_time_results[key][event_inds][:, window_inds] \
                for key in self.event_time_results}

        return output

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


    @copy_doc_func_to_method(save_group)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        fg = SpectralGroupModel(*self.get_settings())
        fg.add_meta_data(self.get_meta_data())

        if save_settings and not save_results and not save_data:
            fg.save(file_name, file_path, save_settings=True)
        else:
            ndigits = len(str(len(self)))
            for ind, gres in enumerate(self.event_group_results):
                fg.group_results = gres
                if save_data:
                    fg.power_spectra = self.spectrograms[ind, :, :].T
                fg.save(file_name + '_{:0{ndigits}d}'.format(ind, ndigits=ndigits),
                        file_path=file_path, save_results=save_results,
                        save_settings=save_settings, save_data=save_data)


    def load(self, file_name, file_path=None, peak_org=None):
        """Load data from file(s).

        Parameters
        ----------
        file_name : str
            File(s) to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        peak_org : int or Bands, optional
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        files = get_files(file_path, select=file_name)
        for file in files:
            super().load(file, file_path, peak_org=False)
            if self.group_results:
                self.event_group_results.append(self.group_results)

        self._reset_group_results()
        if peak_org is not False:
            self.convert_results(peak_org)


    def get_model(self, event_ind, window_ind, regenerate=True):
        """Get a model fit object for a specified index.

        Parameters
        ----------
        event_ind : int
            Index for which event to extract from.
        window_ind : int
            Index for which time window to extract from.
        regenerate : bool, optional, default: False
            Whether to regenerate the model fits for the requested model.

        Returns
        -------
        model : SpectralModel
            The FitResults data loaded into a model object.
        """

        # Initialize a model object, with same settings & check data mode as current object
        model = SpectralModel(*self.get_settings(), verbose=self.verbose)
        model.set_check_data_mode(self._check_data)

        # Add data for specified single power spectrum, if available
        #   The power spectrum is inverted back to linear, as it is re-logged when added to object
        if self.has_data:
            model.add_data(self.freqs, np.power(10, self.spectrograms[event_ind][:, window_ind]))
        # If no power spectrum data available, copy over data information & regenerate freqs
        else:
            model.add_meta_data(self.get_meta_data())

        # Add results for specified power spectrum, regenerating full fit if requested
        model.add_results(self.event_group_results[event_ind][window_ind])
        if regenerate:
            model._regenerate_model()

        return model


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


    def to_df(self, peak_org=None):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        peak_org : int or Bands, optional
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
            If provided, re-extracts peak features; if not provided, converts from `time_results`.

        Returns
        -------
        pd.DataFrame
            Model results organized into a pandas object.
        """

        if peak_org is not None:
            df = event_group_to_dataframe(self.event_group_results, peak_org)
        else:
            df = dict_to_df(flatten_results_dict(self.get_results()))

        return df


    def convert_results(self, peak_org):
        """Convert the event results to be organized across events and time windows.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        self.event_time_results = event_group_to_dict(self.event_group_results, peak_org)


def _par_fit(spectrogram, model):
    """Helper function for running in parallel."""

    model.power_spectra = spectrogram.T
    model.fit(peak_org=False)

    return model.group_results
