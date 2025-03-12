"""Group model object and associated code for fitting the model to 2D groups of power spectra.

Notes
-----
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

from specparam.objs.base import BaseObject2D
from specparam.objs.model import SpectralModel
from specparam.objs.algorithm import SpectralFitAlgorithm
from specparam.plts.group import plot_group_model
from specparam.reports.save import save_group_report
from specparam.reports.strings import gen_group_results_str
from specparam.modutils.docs import (copy_doc_func_to_method,
                                     docs_get_section, replace_docstring_sections)
from specparam.data.conversions import group_to_dataframe

###################################################################################################
###################################################################################################

@replace_docstring_sections([docs_get_section(SpectralModel.__doc__, 'Parameters'),
                             docs_get_section(SpectralModel.__doc__, 'Notes')])
class SpectralGroupModel(SpectralFitAlgorithm, BaseObject2D):
    """Model a group of power spectra as a combination of aperiodic and periodic components.

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
    %copied in from SpectralModel object
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

        BaseObject2D.__init__(self,
                              aperiodic_mode=kwargs.pop('aperiodic_mode', 'fixed'),
                              periodic_mode=kwargs.pop('periodic_mode', 'gaussian'),
                              debug_mode=kwargs.pop('debug_mode', False),
                              verbose=kwargs.pop('verbose', True))

        SpectralFitAlgorithm.__init__(self, *args, **kwargs)


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

        return group_to_dataframe(self.get_results(), peak_org)


    def _check_width_limits(self):
        """Check and warn about bandwidth limits / frequency resolution interaction."""

        # Only check & warn on first power spectrum
        #   This is to avoid spamming standard output for every spectrum in the group
        if self.power_spectra[0, 0] == self.power_spectrum[0]:
            super()._check_width_limits()
