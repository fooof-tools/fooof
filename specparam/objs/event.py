"""Event model object and associated code for fitting the model to spectrograms across events."""

import numpy as np

from specparam.objs import SpectralModel, SpectralTimeModel
from specparam.plts.event import plot_event_model
from specparam.data.conversions import group_to_dict
from specparam.data.utils import get_results_by_row
from specparam.core.modutils import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.core.reports import save_event_report
from specparam.core.strings import gen_event_results_str

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
    spectrograms : list of 2d array
        Power values for the spectrograms, which each array as [n_freqs, n_time_windows].
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

        self.spectrograms = []

        self._reset_event_results()


    def __len__(self):
        """Redefine the length of the objects as the number of event results."""

        return len(self.event_group_results)


    def __getitem__(self, ind):
        """Allow for indexing into the object to select fit results for a specific event."""

        return get_results_by_row(self.event_time_results, ind)


    def _reset_event_results(self):
        """Set, or reset, event results to be empty."""

        self.event_group_results = []
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
        spectrograms : list of 2d array, shape=[n_freqs, n_time_windows]
            Matrix of power values, in linear space.
            Each spectrogram should an event, each with the same set of time windows.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If given a list of spectrograms, add to object
        if isinstance(spectrograms, list):

            if np.any(self.freqs):
                self._reset_event_results()
                self.spectrograms = []
            for spectrogram in spectrograms:
                t_freqs, spectrogram, t_freq_range, t_freq_res = \
                    self._prepare_data(freqs, spectrogram.T, freq_range, 2)
                self.spectrograms.append(spectrogram.T)
            self.freqs = t_freqs
            self.freq_range = t_freq_range
            self.freq_res = t_freq_res

        # If input is an array, pass through to underlying object method
        else:
            super().add_data(freqs, spectrograms, freq_range)


    def report(self, freqs=None, spectrograms=None, freq_range=None,
               peak_org=None, n_jobs=1, progress=None):
        """Fit a set of events and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        spectrograms : list of 2d array, shape=[n_freqs, n_time_windows]
            Matrix of power values, in linear space.
            Each spectrogram should an event, each with the same set of time windows.
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
        spectrograms : list of 2d array, shape=[n_freqs, n_time_windows]
            Matrix of power values, in linear space.
            Each spectrogram should an event, each with the same set of time windows.
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

        if spectrograms is not None:
            self.add_data(freqs, spectrograms, freq_range)
        if len(self):
            self._reset_event_results()

        for spectrogram in self.spectrograms:
            self.power_spectra = spectrogram.T
            super().fit()
            self.event_group_results.append(self.group_results)

        self._convert_to_event_results(peak_org)


    def get_results(self):
        """Return the results from across the set of events."""

        return self.event_time_results


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


    def get_model(self, ind, regenerate=True):
        """Get a model fit object for a specified index.

        Parameters
        ----------
        ind : list of [int, int]
            Index to extract, listed as [event_index, time_window_index].
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
            model.add_data(self.freqs, np.power(10, self.spectrograms[ind[0]][:, ind[1]]))
        # If no power spectrum data available, copy over data information & regenerate freqs
        else:
            model.add_meta_data(self.get_meta_data())

        # Add results for specified power spectrum, regenerating full fit if requested
        model.add_results(self.event_group_results[ind[0]][ind[1]])
        if regenerate:
            model._regenerate_model()

        return model


    def _convert_to_event_results(self, peak_org):
        """Convert the event results to be organized across across and time windows.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        temp = group_to_dict(self.event_group_results[0], peak_org)
        for key in temp:
            self.event_time_results[key] = []

        for gres in self.event_group_results:
            dictres = group_to_dict(gres, peak_org)
            for key in dictres:
                self.event_time_results[key].append(dictres[key])

        for key in self.event_time_results:
            self.event_time_results[key] = np.array(self.event_time_results[key])

    # ToDo: check & figure out adding `load` method

    def _convert_to_time_results(self, peak_org):
        """Overrides inherited objects function to void running this conversion per spectrogram."""
        pass
