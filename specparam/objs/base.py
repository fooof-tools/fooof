"""Define common base objects."""

from copy import deepcopy

import numpy as np

from specparam.utils.array import unlog
from specparam.modes.modes import Modes
from specparam.modes.items import OBJ_DESC
from specparam.io.utils import get_files
from specparam.io.files import load_json, load_jsonlines
from specparam.io.models import save_model, save_group, save_event
from specparam.modutils.errors import NoDataError, FitError
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.objs.results import BaseResults, BaseResults2D, BaseResults2DT, BaseResults3D
from specparam.objs.data import BaseData, BaseData2D, BaseData2DT, BaseData3D
from specparam.objs.utils import run_parallel_group, run_parallel_event, pbar

###################################################################################################
###################################################################################################

class CommonBase():
    """Define CommonBase object."""

    def __init__(self, verbose):
        """Initialize object."""

        self.verbose = verbose


    def copy(self):
        """Return a copy of the current object."""

        return deepcopy(self)


    def fit(self, freqs=None, power_spectrum=None, freq_range=None):
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

        # In rare cases, the model fails to fit, and so uses try / except
        try:

            # If not set to fail on NaN or Inf data at add time, check data here
            #   This serves as a catch all for curve_fits which will fail given NaN or Inf
            #   Because FitError's are by default caught, this allows fitting to continue
            if not self.data._check_data:
                if np.any(np.isinf(self.data.power_spectrum)) or np.any(np.isnan(self.data.power_spectrum)):
                    raise FitError("Model fitting was skipped because there are NaN or Inf "
                                   "values in the data, which preclude model fitting.")

            # Call the fit function from the algorithm object
            self._fit()

            # Compute goodness of fit & error measures
            self._compute_model_gof()
            self._compute_model_error()

        except FitError:

            # If in debug mode, re-raise the error
            if self._debug:
                raise

            # Clear any interim model results that may have run
            #   Partial model results shouldn't be interpreted in light of overall failure
            self._reset_results(clear_results=True)

            # Print out status
            if self.verbose:
                print("Model fitting was unsuccessful.")


    def get_data(self, component='full', space='log'):
        """Get a data component.

        Parameters
        ----------
        component : {'full', 'aperiodic', 'peak'}
            Which data component to return.
                'full' - full power spectrum
                'aperiodic' - isolated aperiodic data component
                'peak' - isolated peak data component
        space : {'log', 'linear'}
            Which space to return the data component in.
                'log' - returns in log10 space.
                'linear' - returns in linear space.

        Returns
        -------
        output : 1d array
            Specified data component, in specified spacing.

        Notes
        -----
        The 'space' parameter doesn't just define the spacing of the data component
        values, but rather defines the space of the additive data definition such that
        `power_spectrum = aperiodic_component + peak_component`.
        With space set as 'log', this combination holds in log space.
        With space set as 'linear', this combination holds in linear space.
        """

        if not self.data.has_data:
            raise NoDataError("No data available to fit, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.data.power_spectrum if space == 'log' else unlog(self.data.power_spectrum)
        elif component == 'aperiodic':
            output = self._spectrum_peak_rm if space == 'log' else \
                unlog(self.data.power_spectrum) / unlog(self._peak_fit)
        elif component == 'peak':
            output = self._spectrum_flat if space == 'log' else \
                unlog(self.data.power_spectrum) - unlog(self._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        for key in data.keys():
            if getattr(self, key, False) is not False:
                setattr(self, key, data[key])
            elif getattr(self.data, key, False) is not False:
                setattr(self.data, key, data[key])


    def _check_loaded_modes(self, data):
        """Check if fit modes added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # TEMP / ToDo: not quite clear if this is the right place
        #   And/or - might want a clearer process to 'reset' Modes

        if 'aperiodic_mode' in data and 'periodic_mode' in data:
            self.modes = Modes(aperiodic=data['aperiodic_mode'],
                               periodic=data['periodic_mode'])


class BaseObject(CommonBase, BaseResults):
    """Define Base object for fitting models to 1D data."""

    def __init__(self, verbose=False):
        """Initialize BaseObject object."""

        CommonBase.__init__(self, verbose=verbose)

        self.data = BaseData()

        BaseResults.__init__(self)


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
        self._reset_results(clear_results=self.has_model and clear_results)

        self.data.add_data(freqs, power_spectrum, freq_range=freq_range)


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
        self._check_loaded_settings(data)
        self._check_loaded_results(data)

        # Regenerate model components, based on what is available
        if regenerate:
            if self.data.freq_res:
                self.data._regenerate_freqs()
            if np.all(self.data.freqs) and np.all(self.aperiodic_params_):
                self._regenerate_model()


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
        self._reset_results(clear_results)


class BaseObject2D(CommonBase, BaseResults2D):
    """Define Base object for fitting models to 2D data."""

    def __init__(self, verbose=True):
        """Initialize BaseObject2D object."""

        CommonBase.__init__(self, verbose=verbose)

        self.data = BaseData2D()

        BaseResults2D.__init__(self)


    def add_data(self, freqs, power_spectra, freq_range=None, clear_results=True):
        """Add data (frequencies and power spectrum values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        power_spectra : 2d array, shape=[n_power_spectra, n_freqs]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if clear_results and np.any(self.data.freqs):
            self._reset_data_results(True, True, True, True)
            self._reset_group_results()

        self.data.add_data(freqs, power_spectra, freq_range=freq_range)


    def fit(self, freqs=None, power_spectra=None, freq_range=None, n_jobs=1, progress=None):
        """Fit a group of power spectra.

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

        Notes
        -----
        Data is optional, if data has already been added to the object.
        """

        # If freqs & power spectra provided together, add data to object
        if freqs is not None and power_spectra is not None:
            self.add_data(freqs, power_spectra, freq_range)

        # If 'verbose', print out a marker of what is being run
        if self.verbose and not progress:
            print('Fitting model across {} power spectra.'.format(len(self.data.power_spectra)))

        # Run linearly
        if n_jobs == 1:
            self._reset_group_results(len(self.data.power_spectra))
            for ind, power_spectrum in \
                pbar(enumerate(self.data.power_spectra), progress, len(self)):
                self._pass_through_spectrum(power_spectrum)
                super().fit()
                self.group_results[ind] = self._get_results()

        # Run in parallel
        else:
            self._reset_group_results()
            self.group_results = run_parallel_group(self, self.data.power_spectra, n_jobs, progress)

        # Clear the individual power spectrum and fit results of the current fit
        self._reset_data_results(clear_spectrum=True, clear_results=True)


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

            # If power spectra data is part of loaded data, collect to add to object
            if 'power_spectrum' in data.keys():
                power_spectra.append(data.pop('power_spectrum'))

            self._add_from_dict(data)

            # If settings are loaded, check and update based on the first line
            if ind == 0:
                self._check_loaded_modes(data)
                self._check_loaded_settings(data)

            # If results part of current data added, check and update object results
            if set(OBJ_DESC['results']).issubset(set(data.keys())):
                self._check_loaded_results(data)
                self.group_results.append(self._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.data.freq_range:
            self.data._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.data.power_spectra = np.array(power_spectra)

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(clear_spectrum=True, clear_results=True)


    def _pass_through_spectrum(self, power_spectrum):
        """Pass through a power spectrum to add to object.

        Notes
        -----
        Passing through a spectrum like this assumes there is an existing & consistent frequency
        definition to use and that the power_spectrum is already logged, with correct freq_range.
        This should only be done internally for passing through individual spectra that
        have already undergone data checking during data adding.
        """

        self.data.power_spectrum = power_spectrum


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False,
                            clear_results=False, clear_spectra=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        clear_spectra : bool, optional, default: False
            Whether to clear power spectra attribute.
        """

        self.data._reset_data(clear_freqs, clear_spectrum, clear_spectra)
        self._reset_results(clear_results)


class BaseObject2DT(BaseObject2D, BaseResults2DT):
    """Define Base object for fitting models to 2D data - tranpose version."""

    def __init__(self, verbose=True):
        """Initialize BaseObject2DT object."""

        BaseObject2D.__init__(self, verbose=verbose)

        self.data = BaseData2DT()

        BaseResults2D.__init__(self)


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
            self.convert_results(peak_org)


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
        self._reset_time_results()
        super().load(file_name, file_path=file_path)
        if peak_org is not False and self.group_results:
            self.convert_results(peak_org)


class BaseObject3D(BaseObject2DT, BaseResults3D):
    """Define Base object for fitting models to 3D data."""

    def __init__(self, verbose=True):
        """Initialize BaseObject3D object."""

        BaseObject2DT.__init__(self, verbose=verbose)

        self.data = BaseData3D()

        BaseResults3D.__init__(self)


    def add_data(self, freqs, spectrograms, freq_range=None, clear_results=True):
        """Add data (frequencies and spectrograms) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        spectrograms : 3d array or list of 2d array
            Matrix of power values, in linear space.
            If a list of 2d arrays, each should be have the same shape of [n_freqs, n_time_windows].
            If a 3d array, should have shape [n_events, n_freqs, n_time_windows].
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results these will be cleared
        by this method call, unless explicitly set not to.
        """

        if clear_results:
            self._reset_event_results()

        self.data.add_data(freqs, spectrograms, freq_range=freq_range)


    def fit(self, freqs=None, spectrograms=None, freq_range=None, peak_org=None,
            n_jobs=1, progress=None):
        """Fit a set of events.

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

        if spectrograms is not None:
            self.add_data(freqs, spectrograms, freq_range)

        # If 'verbose', print out a marker of what is being run
        if self.verbose and not progress:
            print('Fitting model across {} events of {} windows.'.format(\
                len(self.data.spectrograms), self.data.n_time_windows))

        if n_jobs == 1:
            self._reset_event_results(len(self.data.spectrograms))
            for ind, spectrogram in pbar(enumerate(self.data.spectrograms), progress, len(self)):
                self.data.power_spectra = spectrogram.T
                super().fit(peak_org=False)
                self.event_group_results[ind] = self.group_results
                self._reset_group_results()
                self._reset_data_results(clear_spectra=True)

        else:
            fg = self.get_group(None, None, 'group')
            self.event_group_results = run_parallel_event(fg, self.data.spectrograms, n_jobs, progress)

        if peak_org is not False:
            self.convert_results(peak_org)


    @copy_doc_func_to_method(save_event)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_event(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None, peak_org=None):
        """Load data from file(s).

        Parameters
        ----------
        file_name : str
            File(s) to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        peak_org : int or Bands, optional
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        files = get_files(file_path, select=file_name)
        spectrograms = []
        for file in files:
            super().load(file, file_path, peak_org=False)
            if self.group_results:
                self.add_results(self.group_results, append=True)
            if np.all(self.data.power_spectra):
                spectrograms.append(self.data.spectrogram)
        self.data.spectrograms = np.array(spectrograms) if spectrograms else None

        self._reset_group_results()
        if peak_org is not False and self.event_group_results:
            self.convert_results(peak_org)


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False, clear_results=False,
                            clear_spectra=False, clear_spectrograms=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        clear_spectra : bool, optional, default: False
            Whether to clear power spectra attribute.
        clear_spectrograms : bool, optional, default: False
            Whether to clear spectrograms attribute.
        """

        self.data._reset_data(clear_freqs, clear_spectrum, clear_spectra, clear_spectrograms)
        self._reset_results(clear_results)
