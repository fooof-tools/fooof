"""Model object, which defines the power spectrum model.

Code Notes
----------
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

import numpy as np

from specparam.modes.modes import Modes
from specparam.models.base import BaseModel
from specparam.objs.data import BaseData
from specparam.objs.results import BaseResults
from specparam.algorithms.spectral_fit import SpectralFitAlgorithm, SPECTRAL_FIT_SETTINGS
from specparam.reports.save import save_model_report
from specparam.reports.strings import gen_model_results_str
from specparam.modutils.errors import NoModelError
from specparam.modutils.docs import (copy_doc_func_to_method, replace_docstring_sections,
                                     docs_get_section)
from specparam.io.files import load_json
from specparam.io.models import save_model
from specparam.plts.model import plot_model
from specparam.data.utils import get_model_params
from specparam.data.conversions import model_to_dataframe

###################################################################################################
###################################################################################################

@replace_docstring_sections([SPECTRAL_FIT_SETTINGS.make_docstring()])
class SpectralModel(BaseModel):
    """Model a power spectrum as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    % copied in from Spectral Fit Algorithm Settings
    aperiodic_mode : {'fixed', 'knee'}
        Which approach to take for fitting the aperiodic component.
    periodic_mode : {'gaussian', 'skewed_gaussian', 'cauchy'}
        Which approach to take for fitting the periodic component.
    verbose : bool, optional, default: True
        Verbosity mode. If True, prints out warnings and general status updates.
    **model_kwargs
        Additional model fitting related keyword arguments.

    Attributes
    ----------
    freqs : 1d array
        Frequency values for the power spectrum.
    power_spectrum : 1d array
        Power values, stored internally in log10 scale.
    freq_range : list of [float, float]
        Frequency range of the power spectrum, as [lowest_freq, highest_freq].
    freq_res : float
        Frequency resolution of the power spectrum.
    modeled_spectrum_ : 1d array
        The full model fit of the power spectrum, in log10 scale.
    aperiodic_params_ : 1d array
        Fitted parameter values that define the aperiodic fit. As [Offset, (Knee), Exponent].
        The knee parameter is only included if aperiodic component is fit with a knee.
    peak_params_ : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CF, PW, BW].
    gaussian_params_ : 2d array
        Fitted parameter values that define the gaussian fit(s).
        Each row is a gaussian, as [mean, height, standard deviation].
    r_squared_ : float
        R-squared of the fit between the input power spectrum and the full model fit.
    error_ : float
        Error of the full model fit.
    n_peaks_ : int
        The number of peaks fit in the model.
    has_data : bool
        Whether data is loaded to the object.
    has_model : bool
        Whether model results are available in the object.
    _gof_metric : str
        The goodness of fit metric to use for post-hoc measures of model fit.
    _error_metric : str
        The error metric to use for post-hoc measures of model fit error.
        Note: this is for checking error post fitting, not an objective function for fitting.
    _debug : bool
        Whether the object is set in debug mode.
        If in debug mode, an error is raised if model fitting is unsuccessful.
        This should be controlled by using the `set_debug` method.

    Notes
    -----
    - Commonly used abbreviations used in this module include:
      CF: center frequency, PW: power, BW: Bandwidth, AP: aperiodic
    - Input power spectra must be provided in linear scale.
      Internally they are stored in log10 scale, as this is what the model operates upon.
    - Input power spectra should be smooth, as overly noisy power spectra may lead to bad fits.
      For example, raw FFT inputs are not appropriate. Where possible and appropriate, use
      longer time segments for power spectrum calculation to get smoother power spectra,
      as this will give better model fits.
    - The gaussian params are those that define the gaussian of the fit, where as the peak
      params are a modified version, in which the CF of the peak is the mean of the gaussian,
      the PW of the peak is the height of the gaussian over and above the aperiodic component,
      and the BW of the peak, is 2*std of the gaussian (as 'two sided' bandwidth).
    """

    def __init__(self, peak_width_limits=(0.5, 12.0), max_n_peaks=np.inf, min_peak_height=0.0,
                 peak_threshold=2.0, aperiodic_mode='fixed', periodic_mode='gaussian',
                 verbose=True, **model_kwargs):
        """Initialize model object."""

        BaseModel.__init__(self, verbose=verbose)

        self.modes = Modes(aperiodic=aperiodic_mode, periodic=periodic_mode)

        self.data = BaseData()

        self.results = BaseResults(modes=self.modes)

        self.algorithm = SpectralFitAlgorithm(peak_width_limits=peak_width_limits,
            max_n_peaks=max_n_peaks, min_peak_height=min_peak_height,
            peak_threshold=peak_threshold,
            data=self.data, modes=self.modes, results=self.results, verbose=self.verbose,
            **model_kwargs)


    @replace_docstring_sections([docs_get_section(BaseData.add_data.__doc__, 'Parameters'),
                                 docs_get_section(BaseData.add_data.__doc__, 'Notes')])
    def add_data(self, freqs, power_spectrum, freq_range=None, clear_results=True):
        """Add data (frequencies, and power spectrum values) to the current object.

        Parameters
        ----------
        % copied in from Data object
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        % copied in from Data object
        """

        # Clear results, if present, unless indicated not to
        self.results._reset_results(self.results.has_model and clear_results)

        self.data.add_data(freqs, power_spectrum, freq_range=freq_range)


    def report(self, freqs=None, power_spectrum=None, freq_range=None,
               plt_log=False, plot_full_range=False, **plot_kwargs):
        """Run model fit, and display a report, which includes a plot, and printed results.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum.
        power_spectrum : 1d array, optional
            Power values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to fit the model to.
            If not provided, fits across the entire given range.
        plt_log : bool, optional, default: False
            Whether or not to plot the frequency axis in log space.
        plot_full_range : bool, default: False
            If True, plots the full range of the given power spectrum.
            Only relevant / effective if `freqs` and `power_spectrum` passed in in this call.
        **plot_kwargs
            Keyword arguments to pass into the plot method.
            Plot options with a name conflict be passed by pre-pending 'plot_'.
            e.g. `freqs`, `power_spectrum` and `freq_range`.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        self.fit(freqs, power_spectrum, freq_range)
        self.plot(plt_log=plt_log,
                  freqs=freqs if plot_full_range else plot_kwargs.pop('plot_freqs', None),
                  power_spectrum=power_spectrum if \
                      plot_full_range else plot_kwargs.pop('plot_power_spectrum', None),
                  freq_range=plot_kwargs.pop('plot_freq_range', None),
                  **plot_kwargs)
        self.print_results(concise=False)


    def print_results(self, concise=False):
        """Print out model fitting results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_model_results_str(self, concise))


    def get_params(self, name, col=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract.
        col : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
            Column name / index to extract from selected data, if requested.
            Only used for name of {'aperiodic_params', 'peak_params', 'gaussian_params'}.

        Returns
        -------
        out : float or 1d array
            Requested data.

        Raises
        ------
        NoModelError
            If there are no model fit parameters available to return.

        Notes
        -----
        If there are no fit peak (no peak parameters), this method will return NaN.
        """

        if not self.results.has_model:
            raise NoModelError("No model fit results are available to extract, can not proceed.")

        return get_model_params(self.results.get_results(), name, col)


    @copy_doc_func_to_method(plot_model)
    def plot(self, plot_peaks=None, plot_aperiodic=True, freqs=None, power_spectrum=None,
             freq_range=None, plt_log=False, add_legend=True, ax=None, data_kwargs=None,
             model_kwargs=None, aperiodic_kwargs=None, peak_kwargs=None, **plot_kwargs):

        plot_model(self, plot_peaks=plot_peaks, plot_aperiodic=plot_aperiodic, freqs=freqs,
                   power_spectrum=power_spectrum, freq_range=freq_range, plt_log=plt_log,
                   add_legend=add_legend, ax=ax, data_kwargs=data_kwargs, model_kwargs=model_kwargs,
                   aperiodic_kwargs=aperiodic_kwargs, peak_kwargs=peak_kwargs, **plot_kwargs)


    @copy_doc_func_to_method(save_model)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_model(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None, regenerate=True):
        """Load in a data file to the current object.

        Parameters
        ----------
        file_name : str or FileObject
            File to load data from.
        file_path : Path or str, optional
            Path to directory to load from. If None, loads from current directory.
        regenerate : bool, optional, default: True
            Whether to regenerate the model fit from the loaded data, if data is available.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data_results(True, True, True)

        # Load JSON file
        data = load_json(file_name, file_path)

        # Add loaded data to object and check loaded data
        self._add_from_dict(data)
        self._check_loaded_modes(data)
        self.algorithm._check_loaded_settings(data)
        self.results._check_loaded_results(data)

        # Regenerate model components, based on what is available
        if regenerate:
            if self.data.freq_res:
                self.data._regenerate_freqs()
            if np.all(self.data.freqs) and np.all(self.results.aperiodic_params_):
                self.results._regenerate_model(self.data.freqs)


    @copy_doc_func_to_method(save_model_report)
    def save_report(self, file_name, file_path=None, add_settings=True, **plot_kwargs):

        save_model_report(self, file_name, file_path, add_settings, **plot_kwargs)


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
        pd.Series
            Model results organized into a pandas object.
        """

        return model_to_dataframe(self.results.get_results(), peak_org)


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False, clear_results=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        self.data._reset_data(clear_freqs, clear_spectrum)
        self.results._reset_results(clear_results)
