"""Time model object and associated code for fitting the model to spectrograms."""

import numpy as np

from specparam.modes.modes import Modes
from specparam.models import SpectralModel
from specparam.objs.base import BaseObject2DT
from specparam.algorithms.spectral_fit import SpectralFitAlgorithm
from specparam.data.conversions import group_to_dataframe, dict_to_df
from specparam.plts.time import plot_time_model
from specparam.reports.save import save_time_report
from specparam.reports.strings import gen_time_results_str
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralTimeModel(BaseObject2DT):
    """Model a spectrogram as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    % copied in from SpectralModel object

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the spectrogram.
    spectrogram : 2d array
        Power values for the spectrogram, as [n_freqs, n_time_windows].
        Power values are stored internally in log10 scale.
    freq_range : list of [float, float]
        Frequency range of the spectrogram, as [lowest_freq, highest_freq].
    freq_res : float
        Frequency resolution of the spectrogram.
    time_results : dict
        Results of the model fit across each time window.

    Notes
    -----
    % copied in from SpectralModel object
    - The time object inherits from the group model, which in turn inherits from the
      model object. As such it also has data attributes defined on the model object,
      as well as additional attributes that are added to the group object (see notes
      and attribute list in SpectralGroupModel).
    - Notably, while this object organizes the results into the `time_results`
      attribute, which may include sub-selecting peaks per band (depending on settings)
      the `group_results` attribute is also available, which maintains the full
      model results.
    """

    def __init__(self, *args, **kwargs):
        """Initialize object with desired settings."""

        self.modes = Modes(aperiodic=kwargs.pop('aperiodic_mode', 'fixed'),
                           periodic=kwargs.pop('periodic_mode', 'gaussian'))

        BaseObject2DT.__init__(self, modes=self.modes, verbose=kwargs.pop('verbose', True))

        self.algorithm = SpectralFitAlgorithm(*args, **kwargs,
            data=self.data, modes=self.modes, results=self.results, verbose=self.verbose)

        self.results._reset_time_results()


    def report(self, freqs=None, spectrogram=None, freq_range=None,
               peak_org=None, report_type='time', n_jobs=1, progress=None):
        """Fit a spectrogram and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the spectrogram, in linear space.
        spectrogram : 2d array, shape: [n_freqs, n_time_windows], optional
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

        self.fit(freqs, spectrogram, freq_range, peak_org, n_jobs=n_jobs, progress=progress)
        self.plot(report_type)
        self.print_results(report_type)


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
            df = group_to_dataframe(self.results.group_results, peak_org)
        else:
            df = dict_to_df(self.results.get_results())

        return df


    def _fit_prechecks(self):
        """Overloads fit prechecks.

        Notes
        -----
        This overloads fit prechecks to only run once (on the first spectrum), to avoid
        checking and reporting on every spectrum and repeatedly re-raising the same warning.
        """

        if np.all(self.data.power_spectrum == self.data.spectrogram[:, 0]):
            super()._fit_prechecks()
