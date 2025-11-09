"""Time model object and associated code for fitting the model to spectrograms."""

from specparam.models import SpectralModel, SpectralGroupModel
from specparam.results.results import Results2DT
from specparam.data.data import Data2DT
from specparam.data.conversions import group_to_dataframe, dict_to_df
from specparam.data.utils import get_results_by_ind
from specparam.io.models import save_time
from specparam.plts.time import plot_time_model
from specparam.reports.save import save_time_report
from specparam.reports.strings import gen_time_results_str
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.utils.checks import check_inds

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Attributes'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralTimeModel(SpectralGroupModel):
    """Model a spectrogram as a combination of aperiodic and periodic components.

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
    - The time object inherits from the group model, overwriting the `data` and
      `results` objects with versions for fitting models across time. Temporally
      organized results are collected into the `results.time_results` attribute,
      which may include sub-selecting peaks per band (depending on settings).
      Note that the `results.group_results` attribute is also available, which maintains
      the full model results.
    """

    def __init__(self, *args, **kwargs):
        """Initialize time model object."""

        SpectralGroupModel.__init__(self, *args,
                                    aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                                    periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                                    verbose=kwargs.pop('verbose', True),
                                    **kwargs)

        self.data = Data2DT()

        self.results = Results2DT(modes=self.modes,
                                  metrics=kwargs.pop('metrics', None),
                                  bands=kwargs.pop('bands', None))

        self.algorithm._reset_subobjects(data=self.data, results=self.results)


    def fit(self, freqs=None, spectrogram=None, freq_range=None, bands=None,
            n_jobs=1, progress=None, prechecks=True, convert_results=True):
        """Fit a spectrogram.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the spectrogram, in linear space.
        spectrogram : 2d array, shape: [n_freqs, n_time_windows], optional
            Spectrogram of power spectrum values, in linear space.
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

        if freqs is not None and spectrogram is not None:
            super().add_data(freqs, spectrogram, freq_range)

        if prechecks:
            self.algorithm._fit_prechecks(self.verbose)

        super().fit(n_jobs=n_jobs, progress=progress, prechecks=False)

        if convert_results:
            self.convert_results(bands)


    def report(self, freqs=None, spectrogram=None, freq_range=None,
               bands=None, report_type='time', n_jobs=1, progress=None):
        """Fit a spectrogram and display a report, with a plot and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the spectrogram, in linear space.
        spectrogram : 2d array, shape: [n_freqs, n_time_windows], optional
            Spectrogram of power spectrum values, in linear space.
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

        self.fit(freqs, spectrogram, freq_range, bands, n_jobs=n_jobs, progress=progress)
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


    @copy_doc_func_to_method(save_time)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_time(self, file_name, file_path, append, save_results, save_settings, save_data)


    @copy_doc_func_to_method(save_time_report)
    def save_report(self, file_name, file_path=None, add_settings=True):

        save_time_report(self, file_name, file_path, add_settings)


    def load(self, file_name, file_path=None, convert_results=True):
        """Load time data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        convert_results : bool, optional, default: True
            Whether to convert results to be organized over time.
        """

        # Clear results so as not to have possible prior results interfere
        self.results._reset_time_results()
        super().load(file_name, file_path=file_path)
        if convert_results and self.results.bands and self.results.group_results:
            self.results.convert_results()


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


    def to_df(self, bands=None):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        bands : Bands or dict or int, optional
            How to organize peaks into bands.
            If Bands or dict, uses band definitions. If int, extracts the first 'n' peaks.
            If provided, re-extracts peak features; if not, converts from `time_results`.

        Returns
        -------
        pd.DataFrame
            Model results organized into a pandas object.
        """

        if bands is not None:
            df = group_to_dataframe(self.results.group_results, self.modes, bands)
        else:
            df = dict_to_df(self.results.get_results())

        return df


    def convert_results(self, bands):
        """Convert results to be organized across time.

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
