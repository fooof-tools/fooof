"""Time model object and associated code for fitting the model to spectrograms."""

import numpy as np

from specparam.modes.modes import Modes
from specparam.models import SpectralModel, SpectralGroupModel
from specparam.objs.results import BaseResults2DT
from specparam.objs.data import BaseData2DT
from specparam.algorithms.spectral_fit import SpectralFitAlgorithm
from specparam.data.conversions import group_to_dataframe, dict_to_df
from specparam.data.utils import get_results_by_ind
from specparam.plts.time import plot_time_model
from specparam.reports.save import save_time_report
from specparam.reports.strings import gen_time_results_str
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.utils.checks import check_inds

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralTimeModel(SpectralGroupModel):
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
        """Initialize time model object."""

        SpectralGroupModel.__init__(self, *args,
                                    aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                                    periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                                    verbose=kwargs.pop('verbose', True),
                                    **kwargs)

        self.data = BaseData2DT()
        self.results = BaseResults2DT(modes=self.modes)

        self.algorithm = SpectralFitAlgorithm(*args, **kwargs,
            data=self.data, modes=self.modes, results=self.results, verbose=self.verbose)


    def fit(self, freqs=None, spectrogram=None, freq_range=None, peak_org=None,
            n_jobs=1, progress=None):
        """Fit a spectrogram.

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

        super().fit(freqs, spectrogram, freq_range, n_jobs, progress)
        if peak_org is not False:
            self.results.convert_results(peak_org)


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


    def load(self, file_name, file_path=None, peak_org=None):
        """Load time data from file.

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
        self.results._reset_time_results()
        super().load(file_name, file_path=file_path)
        if peak_org is not False and self.results.group_results:
            self.results.convert_results(peak_org)


    def get_group(self, inds, output_type='time'):
        """Get a new model object with the specified sub-selection of model fits.

        Parameters
        ----------
        inds : array_like of int or array_like of bool
            Indices to extract from the object.
        output_type : {'time', 'group'}, optional
            Type of model object to extract:
                'time' : SpectralTimeObject
                'group' : SpectralGroupObject

        Returns
        -------
        output : SpectralTimeModel or SpectralGroupModel
            The requested selection of results data loaded into a new model object.
        """

        if output_type == 'time':

            # Local import - avoid circularity
            from specparam.models.utils import initialize_model_from_source

            # Initialize a new model object, with same settings as current object
            output = initialize_model_from_source(self, 'time')

            if inds is not None:

                # Check and convert indices encoding to list of int
                inds = check_inds(inds)

                # Add data for specified power spectra, if available
                if self.data.has_data:
                    output.data.power_spectra = self.data.power_spectra[inds, :]

                # Add results for specified power spectra
                output.results.group_results = [self.results.group_results[ind] for ind in inds]
                output.results.time_results = get_results_by_ind(self.results.time_results, inds)

        if output_type == 'group':
            output = super().get_group(inds)

        return output


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
