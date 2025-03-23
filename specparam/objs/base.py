"""Define common base objects."""

from copy import deepcopy

import numpy as np

from specparam.utils.array import unlog
from specparam.utils.checks import check_inds
from specparam.modes.modes import Modes
from specparam.modes.items import OBJ_DESC
from specparam.data.utils import get_results_by_ind
from specparam.io.utils import get_files
from specparam.io.files import load_json, load_jsonlines
from specparam.io.models import save_model, save_group, save_event
from specparam.modutils.errors import NoDataError, FitError
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.objs.results import BaseResults, BaseResults2D, BaseResults2DT, BaseResults3D
from specparam.objs.data import BaseData, BaseData2D, BaseData2DT, BaseData3D
from specparam.objs.utils import run_parallel_group, run_parallel_event, pbar
from specparam.objs.metrics import Metrics

###################################################################################################
###################################################################################################

class CommonBase():
    """Define CommonBase object."""

    def __init__(self, verbose):
        """Initialize object."""

        self.metrics = Metrics()
        self.metrics.set_defaults()

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

            # Compute post-fit metrics
            self.metrics.compute_metrics(self.data, self.results)

        except FitError:

            # If in debug mode, re-raise the error
            if self._debug:
                raise

            # Clear any interim model results that may have run
            #   Partial model results shouldn't be interpreted in light of overall failure
            self.results._reset_results(True)

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
            output = self.results._spectrum_peak_rm if space == 'log' else \
                unlog(self.data.power_spectrum) / unlog(self.results._peak_fit)
        elif component == 'peak':
            output = self.results._spectrum_flat if space == 'log' else \
                unlog(self.data.power_spectrum) - unlog(self.results._ap_fit)
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
            elif getattr(self.results, key, False) is not False:
                setattr(self.results, key, data[key])


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


class BaseObject(CommonBase):
    """Define Base object for fitting models to 1D data."""

    def __init__(self, modes=None, verbose=False):
        """Initialize BaseObject object."""

        CommonBase.__init__(self, verbose=verbose)

        self.data = BaseData()
        self.results = BaseResults(modes=modes)


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
        self.results._check_loaded_results(data)

        # Regenerate model components, based on what is available
        if regenerate:
            if self.data.freq_res:
                self.data._regenerate_freqs()
            if np.all(self.data.freqs) and np.all(self.results.aperiodic_params_):
                self.results._regenerate_model(self.data.freqs)


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


class BaseObject2D(CommonBase):
    """Define Base object for fitting models to 2D data."""

    def __init__(self, modes=None, verbose=True):
        """Initialize BaseObject2D object."""

        CommonBase.__init__(self, verbose=verbose)

        self.data = BaseData2D()
        self.results = BaseResults2D(modes=modes)


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
            self.results._reset_group_results()

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
            self.results._reset_group_results(len(self.data.power_spectra))
            for ind, power_spectrum in \
                pbar(enumerate(self.data.power_spectra), progress, len(self.results)):
                self._pass_through_spectrum(power_spectrum)
                super().fit()
                self.results.group_results[ind] = self.results._get_results()

        # Run in parallel
        else:
            self.results._reset_group_results()
            self.results.group_results = run_parallel_group(self, self.data.power_spectra, n_jobs, progress)

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
        self.results._reset_group_results()

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
                self.results._check_loaded_results(data)
                self.results.group_results.append(self.results._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.data.freq_range:
            self.data._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.data.power_spectra = np.array(power_spectra)

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
            The data and fit results loaded into a model object.
        """

        # Local import - avoid circular
        from specparam import SpectralModel

        # Initialize model object, with same settings, metadata, & check mode as current object
        model = SpectralModel(**self.get_settings()._asdict(), verbose=self.verbose)
        model.data.add_meta_data(self.data.get_meta_data())
        model.data.set_checks(*self.data.get_checks())
        model.set_debug(self.get_debug())

        # Add data for specified single power spectrum, if available
        if self.data.has_data:
            model.data.power_spectrum = self.data.power_spectra[ind]

        # Add results for specified power spectrum, regenerating full fit if requested
        model.results.add_results(self.results.group_results[ind])
        if regenerate:
            model.results._regenerate_model(self.data.freqs)

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

        # Local import - avoid circular
        from specparam import SpectralGroupModel

        # Initialize a new model object, with same settings as current object
        group = SpectralGroupModel(**self.get_settings()._asdict(), verbose=self.verbose)
        group.data.add_meta_data(self.data.get_meta_data())
        group.data.set_checks(*self.data.get_checks())
        group.set_debug(self.get_debug())

        if inds is not None:

            # Check and convert indices encoding to list of int
            inds = check_inds(inds)

            # Add data for specified power spectra, if available
            if self.data.has_data:
                group.data.power_spectra = self.data.power_spectra[inds, :]

            # Add results for specified power spectra
            group.results.group_results = [self.results.group_results[ind] for ind in inds]

        return group


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
        self.results._reset_results(clear_results)


class BaseObject2DT(BaseObject2D):
    """Define Base object for fitting models to 2D data - tranpose version."""

    def __init__(self, modes=None, verbose=True):
        """Initialize BaseObject2DT object."""

        BaseObject2D.__init__(self, modes=modes, verbose=verbose)

        self.data = BaseData2DT()
        self.results = BaseResults2DT(modes=modes)


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

            # Local import - avoid circular
            from specparam import SpectralTimeModel

            # Initialize a new model object, with same settings as current object
            output = SpectralTimeModel(**self.get_settings()._asdict(), verbose=self.verbose)
            output.data.add_meta_data(self.data.get_meta_data())

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


class BaseObject3D(BaseObject2DT):
    """Define Base object for fitting models to 3D data."""

    def __init__(self, modes=None, verbose=True):
        """Initialize BaseObject3D object."""

        BaseObject2DT.__init__(self, modes=modes, verbose=verbose)

        self.data = BaseData3D()
        self.results = BaseResults3D(modes=modes)


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
            self.results._reset_event_results()

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
            self.results._reset_event_results(len(self.data.spectrograms))
            for ind, spectrogram in pbar(enumerate(self.data.spectrograms), progress, len(self.results)):
                self.data.power_spectra = spectrogram.T
                super().fit(peak_org=False)
                self.results.event_group_results[ind] = self.results.group_results
                self.results._reset_group_results()
                self._reset_data_results(clear_spectra=True)

        else:
            fg = self.get_group(None, None, 'group')
            self.results.event_group_results = run_parallel_event(fg, self.data.spectrograms, n_jobs, progress)

        if peak_org is not False:
            self.results.convert_results(peak_org)


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
            if self.results.group_results:
                self.results.add_results(self.results.group_results, append=True)
            if np.all(self.data.power_spectra):
                spectrograms.append(self.data.spectrogram)
        self.data.spectrograms = np.array(spectrograms) if spectrograms else None

        self.results._reset_group_results()
        if peak_org is not False and self.results.event_group_results:
            self.results.convert_results(peak_org)


    def get_group(self, event_inds, window_inds, output_type='event'):
        """Get a new model object with the specified sub-selection of model fits.

        Parameters
        ----------
        event_inds, window_inds : array_like of int or array_like of bool or None
            Indices to extract from the object, for event and time windows.
            If None, selects all available indices.
        output_type : {'time', 'group'}, optional
            Type of model object to extract:
                'event' : SpectralTimeEventObject
                'time' : SpectralTimeObject
                'group' : SpectralGroupObject

        Returns
        -------
        output : SpectralTimeEventModel
            The requested selection of results data loaded into a new model object.
        """

        # Local import - avoid circular
        from specparam import SpectralTimeEventModel

        # Check and convert indices encoding to list of int
        einds = check_inds(event_inds, self.data.n_events)
        winds = check_inds(window_inds, self.data.n_time_windows)

        if output_type == 'event':

            # Initialize a new model object, with same settings as current object
            output = SpectralTimeEventModel(**self.get_settings()._asdict(), verbose=self.verbose)
            output.data.add_meta_data(self.data.get_meta_data())

            if event_inds is not None or window_inds is not None:

                # Add data for specified power spectra, if available
                if self.data.has_data:
                    output.data.spectrograms = self.data.spectrograms[einds, :, :][:, :, winds]

                # Add results for specified power spectra - event group results
                temp = [self.results.event_group_results[ei][wi] for ei in einds for wi in winds]
                step = int(len(temp) / len(einds))
                output.results.event_group_results = \
                    [temp[ind:ind+step] for ind in range(0, len(temp), step)]

                # Add results for specified power spectra - event time results
                output.results.event_time_results = \
                    {key : self.results.event_time_results[key][event_inds][:, window_inds] \
                    for key in self.results.event_time_results}

        elif output_type in ['time', 'group']:

            if event_inds is not None or window_inds is not None:

                # Move specified results & data to `group_results` & `power_spectra` for export
                self.results.group_results = \
                    [self.results.event_group_results[ei][wi] for ei in einds for wi in winds]
                if self.data.has_data:
                    self.data.power_spectra = np.hstack(self.data.spectrograms[einds, :, :][:, :, winds]).T

            new_inds = range(0, len(self.results.group_results)) if self.results.group_results else None
            output = super().get_group(new_inds, output_type)

            # Clear the data that was moved for export
            self.results._reset_group_results()
            self._reset_data_results(clear_spectra=True)

        return output


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
        self.results._reset_results(clear_results)
