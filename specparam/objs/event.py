"""Event model object and associated code for fitting the model to spectrograms across events."""

import numpy as np

from specparam.objs import SpectralModel
from specparam.objs.base import BaseObject3D
from specparam.objs.algorithm import SpectralFitAlgorithm
from specparam.plts.event import plot_event_model
from specparam.data.conversions import event_group_to_dataframe, dict_to_df
from specparam.data.utils import flatten_results_dict
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.reports.save import save_event_report
from specparam.reports.strings import gen_event_results_str

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralTimeEventModel(SpectralFitAlgorithm, BaseObject3D):
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

        BaseObject3D.__init__(self,
                              aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                              periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                              debug_mode=kwargs.pop('debug_mode', False),
                              verbose=kwargs.pop('verbose', True))

        SpectralFitAlgorithm.__init__(self, *args, **kwargs)

        self._reset_event_results()


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

        self.fit(freqs, spectrograms, freq_range, peak_org, n_jobs, progress)
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

        # Initialize model object, with same settings, metadata, & check mode as current object
        model = SpectralModel(**self.get_settings()._asdict(), verbose=self.verbose)
        model.add_meta_data(self.get_meta_data())
        model.set_run_modes(*self.get_run_modes())

        # Add data for specified single power spectrum, if available
        if self.has_data:
            model.power_spectrum = self.spectrograms[event_ind][:, window_ind]

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


    def _check_width_limits(self):
        """Check and warn about bandwidth limits / frequency resolution interaction."""

        # Only check & warn on first spectrum
        #   This is to avoid spamming standard output for every spectrogram in the set
        if np.all(self.power_spectrum == self.spectrograms[0, :, 0]):
            super()._check_width_limits()
