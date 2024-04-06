"""Group model object and associated code for fitting the model to 2D groups of power spectra.

Notes
-----
Methods without defined docstrings import docs at runtime, from aliased external functions.
"""

import numpy as np

from specparam.objs.base import BaseObject2D
from specparam.objs.model import SpectralModel
from specparam.objs.algorithm import SpectralFitAlgorithm
from specparam.plts.group import plot_group_model
from specparam.core.items import OBJ_DESC
from specparam.core.utils import check_inds
from specparam.core.errors import NoModelError
from specparam.core.reports import save_group_report
from specparam.core.strings import gen_group_results_str
from specparam.core.io import save_group, load_jsonlines
from specparam.core.modutils import (copy_doc_func_to_method,
                                     docs_get_section, replace_docstring_sections)
from specparam.data.conversions import group_to_dataframe
from specparam.data.utils import get_group_params

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
                              debug_mode=kwargs.pop('debug_mode', 'False'),
                              verbose=kwargs.pop('verbose', 'True'))

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


    def drop(self, inds):
        """Drop one or more model fit results from the object.

        Parameters
        ----------
        inds : int or array_like of int or array_like of bool
            Indices to drop model fit results for.

        Notes
        -----
        This method sets the model fits as null, and preserves the shape of the model fits.
        """

        null_model = SpectralModel(*self.get_settings()).get_results()
        for ind in check_inds(inds):
            self.group_results[ind] = null_model


    def get_params(self, name, col=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract across the group.
        col : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
            Column name / index to extract from selected data, if requested.
            Only used for name of {'aperiodic_params', 'peak_params', 'gaussian_params'}.

        Returns
        -------
        out : ndarray
            Requested data.

        Raises
        ------
        NoModelError
            If there are no model fit results available.
        ValueError
            If the input for the `col` input is not understood.

        Notes
        -----
        When extracting peak information ('peak_params' or 'gaussian_params'), an additional
        column is appended to the returned array, indicating the index that the peak came from.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")

        return get_group_params(self.group_results, name, col)


    @copy_doc_func_to_method(plot_group_model)
    def plot(self, **plot_kwargs):

        plot_group_model(self, **plot_kwargs)


    @copy_doc_func_to_method(save_group_report)
    def save_report(self, file_name, file_path=None, add_settings=True):

        save_group_report(self, file_name, file_path, add_settings)


    @copy_doc_func_to_method(save_group)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_group(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None):
        """Load group data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : Path or str, optional
            Path to directory to load from. If None, loads from current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_group_results()

        power_spectra = []
        for ind, data in enumerate(load_jsonlines(file_name, file_path)):

            self._add_from_dict(data)

            # If settings are loaded, check and update based on the first line
            if ind == 0:
                self._check_loaded_settings(data)

            # If power spectra data is part of loaded data, collect to add to object
            if 'power_spectrum' in data.keys():
                power_spectra.append(data['power_spectrum'])

            # If results part of current data added, check and update object results
            if set(OBJ_DESC['results']).issubset(set(data.keys())):
                self._check_loaded_results(data)
                self.group_results.append(self._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.freq_range:
            self._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.power_spectra = np.array(power_spectra)

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    def get_model(self, ind, regenerate=True):
        """Get a model fit object for a specified index.

        Parameters
        ----------
        ind : int
            The index of the model from `group_results` to access.
        regenerate : bool, optional, default: False
            Whether to regenerate the model fits for the requested model.

        Returns
        -------
        model : SpectralModel
            The FitResults data loaded into a model object.
        """

        # Initialize model object, with same settings, metadata, & check mode as current object
        model = SpectralModel(*self.get_settings(), verbose=self.verbose)
        model.add_meta_data(self.get_meta_data())
        model.set_run_modes(*self.get_run_modes())

        # Add data for specified single power spectrum, if available
        if self.has_data:
            model.power_spectrum = self.power_spectra[ind]

        # Add results for specified power spectrum, regenerating full fit if requested
        model.add_results(self.group_results[ind])
        if regenerate:
            model._regenerate_model()

        return model


    def get_group(self, inds):
        """Get a Group model object with the specified sub-selection of model fits.

        Parameters
        ----------
        inds : array_like of int or array_like of bool
            Indices to extract from the object.

        Returns
        -------
        group : SpectralGroupModel
            The requested selection of results data loaded into a new group model object.
        """

        # Initialize a new model object, with same settings as current object
        group = SpectralGroupModel(*self.get_settings(), verbose=self.verbose)
        group.add_meta_data(self.get_meta_data())
        group.set_run_modes(*self.get_run_modes())

        if inds is not None:

            # Check and convert indices encoding to list of int
            inds = check_inds(inds)

            # Add data for specified power spectra, if available
            if self.has_data:
                group.power_spectra = self.power_spectra[inds, :]

            # Add results for specified power spectra
            group.group_results = [self.group_results[ind] for ind in inds]

        return group


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
