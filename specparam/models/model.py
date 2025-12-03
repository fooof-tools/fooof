"""Model object, which defines the power spectrum model.

Code Notes
----------
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

import numpy as np

from specparam.models.base import BaseModel
from specparam.data.data import Data
from specparam.data.conversions import model_to_dataframe
from specparam.results.results import Results

from specparam.convert.convert import convert_aperiodic_params, convert_periodic_params
from specparam.convert.definitions import update_converters, DEFAULT_CONVERTERS

from specparam.algorithms.spectral_fit import SPECTRAL_FIT_SETTINGS_DEF
from specparam.algorithms.definitions import ALGORITHMS, check_algorithm_definition

from specparam.reports.save import save_model_report
from specparam.reports.strings import gen_model_results_str
from specparam.modutils.errors import NoDataError, FitError
from specparam.modutils.docs import (copy_doc_func_to_method, replace_docstring_sections,
                                     docs_get_section)
from specparam.utils.checks import check_all_none
from specparam.io.files import load_json
from specparam.io.models import save_model
from specparam.plts.model import plot_model

###################################################################################################
###################################################################################################

@replace_docstring_sections([SPECTRAL_FIT_SETTINGS_DEF.make_docstring()])
class SpectralModel(BaseModel):
    """Model a power spectrum as a combination of aperiodic and periodic components.

    WARNING: frequency and power values inputs must be in linear space. Passing in logged
    frequencies and/or power spectra is not detected, and will silently produce incorrect results.

    Parameters
    ----------
    % copied in from Spectral Fit Algorithm Settings
    aperiodic_mode : {'fixed', 'knee'} or Mode
        Which approach to take for fitting the aperiodic component.
    periodic_mode : {'gaussian', 'skewed_gaussian', 'cauchy'} or Mode
        Which approach to take for fitting the periodic component.
    algorithm : {'spectral_fit'} or Algorithm
        The fitting algorithm to use.
    algorithm_settings : dict
        Setting for the algorithm.
    metrics : Metrics or list of Metric or list or str
        Metrics definition(s) to use to evaluate the model.
    converters : dict
        Definition for parameter conversions to apply post fitting.
    bands : Bands or dict or int or None, optional
        Bands object with band definitions, or definition that can be turned into a Bands object.
    debug : bool, optional, default: False
        Whether to run in debug mode.
        If in debug, any errors encountered during fitting will raise an error.
    verbose : bool, optional, default: True
        Verbosity mode. If True, prints out warnings and general status updates.
    **model_kwargs
        Additional model fitting related keyword arguments.
        These are passed into the algorithm object.

    Attributes
    ----------
    algorithm : Algorithm
        Algorithm object with model fitting settings and procedures.
    modes : Modes
        Modes object with fit mode definitions.
    data : Data
        Data object with spectral data and metadata.
    results : Results
        Results object with model fit results and metrics.

    Notes
    -----
    - Input power spectra must be provided in linear scale.
      Internally they are stored in log10 scale, as this is what the model operates upon.
    - Input power spectra should be smooth, as overly noisy power spectra may lead to bad fits.
      For example, raw FFT inputs are not appropriate. Where possible and appropriate, use
      longer time segments for power spectrum calculation to get smoother power spectra,
      as this will give better model fits.
    """

    def __init__(self, aperiodic_mode='fixed', periodic_mode='gaussian',
                 algorithm='spectral_fit', algorithm_settings=None,
                 metrics=None, converters=None, bands=None,
                 debug=False, verbose=True, **model_kwargs):
        """Initialize model object."""

        converters = DEFAULT_CONVERTERS if not converters else \
            update_converters(DEFAULT_CONVERTERS, converters)
        BaseModel.__init__(self, aperiodic_mode, periodic_mode, converters, verbose)

        self.data = Data()

        self.results = Results(modes=self.modes, metrics=metrics, bands=bands)

        algorithm_settings = {} if algorithm_settings is None else algorithm_settings
        self.algorithm = check_algorithm_definition(algorithm, ALGORITHMS)(
            **algorithm_settings, modes=self.modes, data=self.data,
            results=self.results, debug=debug, **model_kwargs)


    @replace_docstring_sections([docs_get_section(Data.add_data.__doc__, 'Parameters'),
                                 docs_get_section(Data.add_data.__doc__, 'Notes')])
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


    def fit(self, freqs=None, power_spectrum=None, freq_range=None, prechecks=True):
        """Fit a power spectrum as a combination of periodic and aperiodic components.

        Parameters
        ----------
        freqs : 1d array, optional
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array, optional
            Power values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to.
            If not provided, keeps the entire range.
        prechecks : bool, optional, default: True
            Whether to run model fitting pre-checks.

        Raises
        ------
        NoDataError
            If no data is available to fit.
        FitError
            If model fitting fails to fit. Only raised in debug mode.

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If freqs & power_spectrum provided together, add data to object.
        if freqs is not None and power_spectrum is not None:
            self.add_data(freqs, power_spectrum, freq_range)

        # Check that data is available
        if not self.data.has_data:
            raise NoDataError("No data available to fit, can not proceed.")

        if prechecks:
            self.algorithm._fit_prechecks(self.verbose)

        # In rare cases, the model fails to fit, and so uses try / except
        try:

            # If not set to fail on NaN or Inf data at add time, check data here
            #   This serves as a catch all for curve_fits which will fail given NaN or Inf
            #   Because FitError's are by default caught, this allows fitting to continue
            if not self.data.checks['data']:
                if np.any(np.isinf(self.data.power_spectrum)) or \
                    np.any(np.isnan(self.data.power_spectrum)):
                    raise FitError("Model fitting was skipped because there are NaN or Inf "
                                   "values in the data, which preclude model fitting.")

            # Call the fit function from the algorithm object
            self.algorithm._fit()

            # Do any parameter conversions
            self._convert_params()

            # Compute post-fit metrics
            self.results.metrics.compute_metrics(self.data, self.results)

        except FitError:

            # If in debug mode, re-raise the error
            if self.algorithm._debug:
                raise

            # Clear any interim model results that may have run
            #   Partial model results shouldn't be interpreted in light of overall failure
            self.results._reset_results(True)

            # Print out status
            if self.verbose:
                print("Model fitting was unsuccessful.")


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

        # If settings are not loaded, clear defaults to not have potentially incorrect values
        if not set(self.algorithm.settings.names).issubset(set(data.keys())):
            self.algorithm.settings.clear()

        # Regenerate model components, based on what is available
        if regenerate:
            if self.data.freq_res:
                self.data._regenerate_freqs()
            if np.all(self.data.freqs) and np.all(self.results.params.aperiodic):
                self.results._regenerate_model(self.data.freqs)


    @copy_doc_func_to_method(Results.get_params)
    def get_params(self, component, field=None):

        return self.results.get_params(component, field)


    @copy_doc_func_to_method(Results.get_metrics)
    def get_metrics(self, category, measure=None):

        return self.results.get_metrics(category, measure)


    @copy_doc_func_to_method(save_model_report)
    def save_report(self, file_name, file_path=None, add_settings=True, **plot_kwargs):

        save_model_report(self, file_name, file_path, add_settings, **plot_kwargs)


    def to_df(self, bands=None):
        """Convert and extract the model results as a pandas object.

        Parameters
        ----------
        bands : Bands or int, optional
            How to organize peaks into bands.
            If Bands, extracts peaks based on band definitions.
            If int, extracts the first n peaks.
            If not provided, uses the bands definition available in the object.

        Returns
        -------
        pd.Series
            Model results organized into a pandas object.
        """

        if not bands:
            bands = self.results.bands

        return model_to_dataframe(self.results.get_results(), self.modes, bands)


    def _convert_params(self):
        """Convert fit parameters."""

        if not check_all_none(self._converters['aperiodic'].values()):
            self.results.params.aperiodic.add_params(\
                'converted', convert_aperiodic_params(self, self._converters['aperiodic']))
        if not check_all_none(self._converters['periodic'].values()):
            self.results.params.periodic.add_params(\
                'converted', convert_periodic_params(self, self._converters['periodic']))


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
