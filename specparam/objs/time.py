"""Time model object and associated code for fitting the model to spectra across time."""

from functools import wraps

import numpy as np

from specparam.objs import SpectralGroupModel
from specparam.plts.time import plot_time_model
from specparam.data.conversions import group_to_dict
from specparam.data.utils import get_results_by_ind
from specparam.core.reports import save_time_report
from specparam.core.modutils import copy_doc_func_to_method, docs_get_section
from specparam.core.strings import gen_time_results_str

###################################################################################################
###################################################################################################

def transpose_arg1(func):
    """Decorator function to transpose the 1th argument input to a function."""

    @wraps(func)
    def decorated(*args, **kwargs):

        if len(args) >= 2:
            args = list(args)
            args[2] = args[2].T if isinstance(args[2], np.ndarray) else args[2]
        if 'power_spectra' in kwargs:
            kwargs['power_spectra'] = kwargs['power_spectra'].T

        return func(*args, **kwargs)

    return decorated


class SpectralTimeModel(SpectralGroupModel):
    """ToDo."""

    def __init__(self, *args, **kwargs):
        """Initialize object with desired settings."""

        SpectralGroupModel.__init__(self, *args, **kwargs)

        self._reset_time_results()


    def __iter__(self):
        """Allow for iterating across the object by stepping across fit results per time window."""

        for ind in range(len(self)):
            yield self[ind]


    def __getitem__(self, ind):
        """Allow for indexing into the object to select fit results for a specific time window."""

        return get_results_by_ind(self.time_results, ind)


    def _reset_time_results(self):
        """Set, or reset, time results to be empty."""

        self.time_results = {}


    @property
    def spectrogram(self):
        """Data attribute view on the power spectra, transposed to spectrogram orientation."""

        return self.power_spectra.T


    @transpose_arg1
    def add_data(self, freqs, spectrogram, freq_range=None):
        """Add data (frequencies and spectrogram values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        spectrogram : 2d array, shape=[n_freqs, n_time_windows]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        if np.any(self.freqs):
            self._reset_time_results()
        super().add_data(freqs, spectrogram, freq_range)


    def report(self, freqs=None, power_spectra=None, freq_range=None,
               peak_org=None, report_type='time', n_jobs=1, progress=None):
        """Fit a group of power spectra and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_freqs, n_time_windows], optional
            Spectrogram of power spectrum values, in linear space.
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

        self.fit(freqs, power_spectra, freq_range, peak_org, n_jobs=n_jobs, progress=progress)
        self.plot(report_type)
        self.print_results(report_type)


    def fit(self, freqs=None, power_spectra=None, freq_range=None, peak_org=None,
            n_jobs=1, progress=None):
        """Fit a spectrogram

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power_spectra, in linear space.
        power_spectra : 2d array, shape: [n_freqs, n_time_windows], optional
            Spectrogram of power spectrum values, in linear space.
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

        super().fit(freqs, power_spectra, freq_range, n_jobs, progress)
        self._convert_to_time_results(peak_org)


    def get_results(self):
        """Return the results run across a spectrogram."""

        return self.time_results


    def print_results(self, print_type='time', concise=False):
        """Print out SpectralTimeModel results.

        Parameters
        ----------
        print_type : {'time', 'group'}
            Which format to print results out in.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        if print_type == 'time':
            print(gen_time_results_str(self, concise))
        if print_type == 'group':
            super().print_results(concise)


    @copy_doc_func_to_method(plot_time_model)
    def plot(self, plot_type='time', save_fig=False, file_name=None, file_path=None, **plot_kwargs):

        if plot_type == 'time':
            plot_time_model(self, save_fig=save_fig, file_name=file_name,
                            file_path=file_path, **plot_kwargs)
        if plot_type == 'group':
            super().plot(save_fig=save_fig, file_name=file_name, file_path=file_path, **plot_kwargs)


    @copy_doc_func_to_method(save_time_report)
    def save_report(self, file_name, file_path=None, add_settings=True):

        save_time_report(self, file_name, file_path, add_settings)


    def load(self, file_name, file_path=None, peak_org=None):
        """Load group data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_time_results()
        super().load(file_name, file_path=file_path)
        self._convert_to_time_results(peak_org)


    def _convert_to_time_results(self, peak_org):
        """Convert the model results into to be organized across time windows.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        self.time_results = group_to_dict(self.group_results, peak_org)
