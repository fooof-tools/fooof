"""Model object, which defines the power spectrum model.

Code Notes
----------
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

from copy import deepcopy

import numpy as np

from specparam.objs.base import BaseSpectralModel
from specparam.core.items import OBJ_DESC
from specparam.core.info import get_indices
from specparam.core.io import save_model, load_json
from specparam.core.reports import save_model_report
from specparam.core.modutils import copy_doc_func_to_method
from specparam.core.utils import check_array_dim
from specparam.core.funcs import infer_ap_func
from specparam.core.errors import NoModelError
from specparam.core.strings import gen_settings_str, gen_model_results_str, gen_issue_str
from specparam.plts.model import plot_model
from specparam.data import FitResults, ModelSettings
from specparam.data.conversions import model_to_dataframe
from specparam.sim.gen import gen_model

###################################################################################################
###################################################################################################

class SpectralModel(BaseSpectralModel):
    """Model a power spectrum as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space.

    Passing in logged frequencies and/or power spectra is not detected,
    and will silently produce incorrect results.

    Parameters
    ----------
    peak_width_limits : tuple of (float, float), optional, default: (0.5, 12.0)
        Limits on possible peak width, in Hz, as (lower_bound, upper_bound).
    max_n_peaks : int, optional, default: inf
        Maximum number of peaks to fit.
    min_peak_height : float, optional, default: 0
        Absolute threshold for detecting peaks.
        This threshold is defined in absolute units of the power spectrum (log power).
    peak_threshold : float, optional, default: 2.0
        Relative threshold for detecting peaks.
        This threshold is defined in relative units of the power spectrum (standard deviation).
    aperiodic_mode : {'fixed', 'knee'}
        Which approach to take for fitting the aperiodic component.
    verbose : bool, optional, default: True
        Verbosity mode. If True, prints out warnings and general status updates.

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
        Parameters that define the aperiodic fit. As [Offset, (Knee), Exponent].
        The knee parameter is only included if aperiodic component is fit with a knee.
    peak_params_ : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CF, PW, BW].
    gaussian_params_ : 2d array
        Parameters that define the gaussian fit(s).
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
                 peak_threshold=2.0, aperiodic_mode='fixed', verbose=True, **model_kwargs):
        """Initialize model object."""

        BaseSpectralModel.__init__(self, peak_width_limits=peak_width_limits,
                                   max_n_peaks=max_n_peaks, min_peak_height=min_peak_height,
                                   peak_threshold=peak_threshold, aperiodic_mode=aperiodic_mode,
                                   verbose=verbose, **model_kwargs)


    @property
    def n_peaks_(self):
        """How many peaks were fit in the model."""

        return self.peak_params_.shape[0] if self.has_model else None


    def add_settings(self, settings):
        """Add settings into object from a ModelSettings object.

        Parameters
        ----------
        settings : ModelSettings
            A data object containing the settings for a power spectrum model.
        """

        for setting in OBJ_DESC['settings']:
            setattr(self, setting, getattr(settings, setting))

        self._check_loaded_settings(settings._asdict())


    def add_results(self, results):
        """Add results data into object from a FitResults object.

        Parameters
        ----------
        results : FitResults
            A data object containing the results from fitting a power spectrum model.
        """

        self.aperiodic_params_ = results.aperiodic_params
        self.gaussian_params_ = results.gaussian_params
        self.peak_params_ = results.peak_params
        self.r_squared_ = results.r_squared
        self.error_ = results.error

        self._check_loaded_results(results._asdict())


    def report(self, freqs=None, power_spectrum=None, freq_range=None,
               plt_log=False, **plot_kwargs):
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
        **plot_kwargs
            Keyword arguments to pass into the plot method.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        self.fit(freqs, power_spectrum, freq_range)
        self.plot(plt_log=plt_log, **plot_kwargs)
        self.print_results(concise=False)


    def print_settings(self, description=False, concise=False):
        """Print out the current settings.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_settings_str(self, description, concise))


    def print_results(self, concise=False):
        """Print out model fitting results.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_model_results_str(self, concise))


    @staticmethod
    def print_report_issue(concise=False):
        """Prints instructions on how to report bugs and/or problematic fits.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_issue_str(concise))


    def get_settings(self):
        """Return user defined settings of the current object.

        Returns
        -------
        ModelSettings
            Object containing the settings from the current object.
        """

        return ModelSettings(**{key : getattr(self, key) \
                             for key in OBJ_DESC['settings']})


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

        if not self.has_model:
            raise NoModelError("No model fit results are available to extract, can not proceed.")

        # If col specified as string, get mapping back to integer
        if isinstance(col, str):
            col = get_indices(self.aperiodic_mode)[col]

        # Allow for shortcut alias, without adding `_params`
        if name in ['aperiodic', 'peak', 'gaussian']:
            name = name + '_params'

        # Extract the request data field from object
        out = getattr(self, name + '_')

        # Periodic values can be empty arrays and if so, replace with NaN array
        if isinstance(out, np.ndarray) and out.size == 0:
            out = np.array([np.nan, np.nan, np.nan])

        # Select out a specific column, if requested
        if col is not None:

            # Extract column, & if result is a single value in an array, unpack from array
            out = out[col] if out.ndim == 1 else out[:, col]
            out = out[0] if isinstance(out, np.ndarray) and out.size == 1 else out

        return out


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics.

        Returns
        -------
        FitResults
            Object containing the model fit results from the current object.
        """

        return FitResults(**{key.strip('_') : getattr(self, key) \
            for key in OBJ_DESC['results']})


    @copy_doc_func_to_method(plot_model)
    def plot(self, plot_peaks=None, plot_aperiodic=True, plt_log=False,
             add_legend=True, save_fig=False, file_name=None, file_path=None,
             ax=None, data_kwargs=None, model_kwargs=None,
             aperiodic_kwargs=None, peak_kwargs=None, **plot_kwargs):

        plot_model(self, plot_peaks=plot_peaks, plot_aperiodic=plot_aperiodic, plt_log=plt_log,
                   add_legend=add_legend, save_fig=save_fig, file_name=file_name,
                   file_path=file_path, ax=ax, data_kwargs=data_kwargs, model_kwargs=model_kwargs,
                   aperiodic_kwargs=aperiodic_kwargs, peak_kwargs=peak_kwargs, **plot_kwargs)


    @copy_doc_func_to_method(save_model_report)
    def save_report(self, file_name, file_path=None, plt_log=False,
                    add_settings=True, **plot_kwargs):

        save_model_report(self, file_name, file_path, plt_log, add_settings, **plot_kwargs)


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
        file_path : str or None, optional
            Path to directory to load from. If None, loads from current directory.
        regenerate : bool, optional, default: True
            Whether to regenerate the model fit from the loaded data, if data is available.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data_results(True, True, True)

        # Load JSON file, add to self and check loaded data
        data = load_json(file_name, file_path)
        self._add_from_dict(data)
        self._check_loaded_settings(data)
        self._check_loaded_results(data)

        # Regenerate model components, based on what is available
        if regenerate:
            if self.freq_res:
                self._regenerate_freqs()
            if np.all(self.freqs) and np.all(self.aperiodic_params_):
                self._regenerate_model()


    def copy(self):
        """Return a copy of the current object."""

        return deepcopy(self)


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

        return model_to_dataframe(self.get_results(), peak_org)


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        # Reconstruct object from loaded data
        for key in data.keys():
            setattr(self, key, data[key])


    def _check_loaded_results(self, data):
        """Check if results have been added and check data.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If results loaded, check dimensions of peak parameters
        #   This fixes an issue where they end up the wrong shape if they are empty (no peaks)
        if set(OBJ_DESC['results']).issubset(set(data.keys())):
            self.peak_params_ = check_array_dim(self.peak_params_)
            self.gaussian_params_ = check_array_dim(self.gaussian_params_)


    def _check_loaded_settings(self, data):
        """Check if settings added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If settings not loaded from file, clear from object, so that default
        # settings, which are potentially wrong for loaded data, aren't kept
        if not set(OBJ_DESC['settings']).issubset(set(data.keys())):

            # Reset all public settings to None
            for setting in OBJ_DESC['settings']:
                setattr(self, setting, None)

            # If aperiodic params available, infer whether knee fitting was used,
            if not np.all(np.isnan(self.aperiodic_params_)):
                self.aperiodic_mode = infer_ap_func(self.aperiodic_params_)

        # Reset internal settings so that they are consistent with what was loaded
        #   Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


    def _regenerate_model(self):
        """Regenerate model fit from parameters."""

        self.modeled_spectrum_, self._peak_fit, self._ap_fit = gen_model(
            self.freqs, self.aperiodic_params_, self.gaussian_params_, return_components=True)
