"""Define base results objects."""

from itertools import repeat

import numpy as np

from specparam.modes.items import OBJ_DESC
from specparam.modes.funcs import infer_ap_func
from specparam.modes.definitions import AP_MODES, PE_MODES
from specparam.utils.array import unlog
from specparam.utils.checks import check_inds, check_array_dim
from specparam.modutils.errors import NoModelError
from specparam.data import FitResults, ModelSettings
from specparam.data.conversions import group_to_dict, event_group_to_dict
from specparam.data.utils import get_group_params, get_results_by_ind, get_results_by_row
from specparam.measures.gof import compute_gof
from specparam.measures.error import compute_error

###################################################################################################
###################################################################################################

class BaseResults():
    """Base object for managing results."""
    # pylint: disable=attribute-defined-outside-init, arguments-differ

    def __init__(self, aperiodic_mode, periodic_mode, debug=False,
                 verbose=True, error_metric='MAE', gof_metric='r_squared'):
        """Initialize BaseResults object."""

        # Set fit component modes
        if isinstance(aperiodic_mode, str):
            self.aperiodic_mode = AP_MODES[aperiodic_mode]
        else:
            self.aperiodic_mode = aperiodic_mode
        if isinstance(periodic_mode, str):
            self.periodic_mode = PE_MODES[periodic_mode]
        else:
            self.periodic_mode = periodic_mode

        # Set run modes
        self.set_debug(debug)
        self.verbose = verbose

        # Initialize results attributes
        self._reset_results(True)

        # Set private run settings
        self._error_metric = error_metric
        self._gof_metric = gof_metric


    @property
    def has_model(self):
        """Indicator for if the object contains a model fit.

        Notes
        -----
        This check uses the aperiodic params, which are:

        - nan if no model has been fit
        - necessarily defined, as floats, if model has been fit
        """

        return True if not np.all(np.isnan(self.aperiodic_params_)) else False


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


    def get_settings(self):
        """Return user defined settings of the current object.

        Returns
        -------
        ModelSettings
            Object containing the settings from the current object.
        """

        return ModelSettings(**{key : getattr(self, key) \
                             for key in OBJ_DESC['settings']})


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


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics.

        Returns
        -------
        FitResults
            Object containing the model fit results from the current object.
        """

        return FitResults(**{key.strip('_') : getattr(self, key) \
            for key in OBJ_DESC['results']})


    def get_model(self, component='full', space='log'):
        """Get a model component.

        Parameters
        ----------
        component : {'full', 'aperiodic', 'peak'}
            Which model component to return.
                'full' - full model
                'aperiodic' - isolated aperiodic model component
                'peak' - isolated peak model component
        space : {'log', 'linear'}
            Which space to return the model component in.
                'log' - returns in log10 space.
                'linear' - returns in linear space.

        Returns
        -------
        output : 1d array
            Specified model component, in specified spacing.

        Notes
        -----
        The 'space' parameter doesn't just define the spacing of the model component
        values, but rather defines the space of the additive model such that
        `model = aperiodic_component + peak_component`.
        With space set as 'log', this combination holds in log space.
        With space set as 'linear', this combination holds in linear space.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.modeled_spectrum_ if space == 'log' else unlog(self.modeled_spectrum_)
        elif component == 'aperiodic':
            output = self._ap_fit if space == 'log' else unlog(self._ap_fit)
        elif component == 'peak':
            output = self._peak_fit if space == 'log' else \
                unlog(self.modeled_spectrum_) - unlog(self._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output


    def set_debug(self, debug):
        """Set debug state, which controls if an error is raised if model fitting is unsuccessful.

        Parameters
        ----------
        debug : bool
            Whether to run in debug state.
        """

        self._debug = debug


    def _check_loaded_modes(self, data):
        """Check if fit modes added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If fit mode information in loaded, reload mode definitions
        self.aperiodic_mode = AP_MODES[data['aperiodic_mode']] \
            if 'aperiodic_mode' in data else None
        self.periodic_mode = PE_MODES[data['periodic_mode']] \
            if 'periodic_mode' in data else None


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

        # Reset internal settings so that they are consistent with what was loaded
        #   Note that this will set internal settings to None, if public settings unavailable
        self._reset_internal_settings()


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


    def _reset_internal_settings(self):
        """"Can be overloaded if any resetting needed for internal settings."""


    def _reset_results(self, clear_results=False):
        """Set, or reset, results attributes to empty.

        Parameters
        ----------
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        if clear_results:

            # Aperiodic parameers
            self.aperiodic_params_ = np.nan

            # Periodic parameters
            self.gaussian_params_ = np.nan
            self.peak_params_ = np.nan

            # Note - for ap / pe params, move to something like `xx_params` and `_xx_params`

            # Goodness of fit measures
            self.r_squared_ = np.nan
            self.error_ = np.nan
            # Note: move to `self.gof` or similar

            # Data components
            self._spectrum_flat = None
            self._spectrum_peak_rm = None

            # Modeled spectrum components
            self.modeled_spectrum_ = None
            self._ap_fit = None
            self._peak_fit = None


    def _compute_model_gof(self, metric=None):
        """Calculate the r-squared goodness of fit of the model, compared to the original data.

        Parameters
        ----------
        metric : {'r_squared', 'adj_r_squared'}, optional
            Which goodness of fit measure to compute:
            * 'r_squared' : R-squared
            * 'adj_r_squared' : Adjusted R-squared

        Notes
        -----
        Which measure is applied is by default controlled by the `_gof_metric` attribute.
        """

        self.r_squared_ = compute_gof(self.power_spectrum, self.modeled_spectrum_)


    def _compute_model_error(self, metric=None):
        """Calculate the overall error of the model fit, compared to the original data.

        Parameters
        ----------
        metric : {'MAE', 'MSE', 'RMSE'}, optional
            Which error measure to compute:
            * 'MAE' : mean absolute error
            * 'MSE' : mean squared error
            * 'RMSE' : root mean squared error

        Notes
        -----
        Which measure is applied is by default controlled by the `_error_metric` attribute.
        """

        self.error_ = compute_error(self.power_spectrum, self.modeled_spectrum_,
                                    self._error_metric if not metric else metric)


class BaseResults2D(BaseResults):
    """Base object for managing results - 2D version."""

    def __init__(self, aperiodic_mode, periodic_mode, debug=False, verbose=True):
        """Initialize BaseResults2D object."""

        BaseResults.__init__(self, aperiodic_mode, periodic_mode, debug=debug, verbose=verbose)

        self._reset_group_results()


    def __len__(self):
        """Define the length of the object as the number of model fit results available."""

        return len(self.group_results)


    def __iter__(self):
        """Allow for iterating across the object by stepping across model fit results."""

        for result in self.group_results:
            yield result


    def __getitem__(self, index):
        """Allow for indexing into the object to select model fit results."""

        return self.group_results[index]


    def _reset_group_results(self, length=0):
        """Set, or reset, results to be empty.

        Parameters
        ----------
        length : int, optional, default: 0
            Length of list of empty lists to initialize. If 0, creates a single empty list.
        """

        self.group_results = [[]] * length


    def _get_results(self):
        """Create an alias to SpectralModel.get_results for the group object, for internal use."""

        return super().get_results()


    @property
    def has_model(self):
        """Indicator for if the object contains model fits."""

        return True if self.group_results else False


    @property
    def n_peaks_(self):
        """How many peaks were fit for each model."""

        return [res.peak_params.shape[0] for res in self] if self.has_model else None


    @property
    def n_null_(self):
        """How many model fits are null."""

        return sum([1 for res in self.group_results if np.isnan(res.aperiodic_params[0])]) \
            if self.has_model else None


    @property
    def null_inds_(self):
        """The indices for model fits that are null."""

        return [ind for ind, res in enumerate(self.group_results) \
            if np.isnan(res.aperiodic_params[0])] \
            if self.has_model else None


    def add_results(self, results):
        """Add results data into object.

        Parameters
        ----------
        results : list of list of FitResults
            List of data objects containing the results from fitting power spectrum models.
        """

        self.group_results = results


    def get_results(self):
        """Return the results run across a group of power spectra."""

        return self.group_results


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

        # Temp import - consider refactoring
        from specparam import SpectralModel

        null_model = SpectralModel(**self.get_settings()._asdict()).get_results()
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

        # Local import - avoid circular
        from specparam import SpectralModel

        # Initialize model object, with same settings, metadata, & check mode as current object
        model = SpectralModel(**self.get_settings()._asdict(), verbose=self.verbose)
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

        # Local import - avoid circular
        from specparam import SpectralGroupModel

        # Initialize a new model object, with same settings as current object
        group = SpectralGroupModel(**self.get_settings()._asdict(), verbose=self.verbose)
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


class BaseResults2DT(BaseResults2D):
    """Base object for managing results - 2D transpose version."""

    def __init__(self, aperiodic_mode, periodic_mode, debug=False, verbose=True):
        """Initialize BaseResults2DT object."""

        BaseResults2D.__init__(self, aperiodic_mode, periodic_mode, debug=debug, verbose=verbose)

        self._reset_time_results()


    def __getitem__(self, ind):
        """Allow for indexing into the object to select fit results for a specific time window."""

        return get_results_by_ind(self.time_results, ind)


    def _reset_time_results(self):
        """Set, or reset, time results to be empty."""

        self.time_results = {}


    def get_results(self):
        """Return the results run across a spectrogram."""

        return self.time_results


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
            output.add_meta_data(self.get_meta_data())

            if inds is not None:

                # Check and convert indices encoding to list of int
                inds = check_inds(inds)

                # Add data for specified power spectra, if available
                if self.has_data:
                    output.power_spectra = self.power_spectra[inds, :]

                # Add results for specified power spectra
                output.group_results = [self.group_results[ind] for ind in inds]
                output.time_results = get_results_by_ind(self.time_results, inds)

        if output_type == 'group':
            output = super().get_group(inds)

        return output


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

        super().drop(inds)
        for key in self.time_results.keys():
            self.time_results[key][inds] = np.nan


    def convert_results(self, peak_org):
        """Convert the model results to be organized across time windows.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        self.time_results = group_to_dict(self.group_results, peak_org)


class BaseResults3D(BaseResults2DT):
    """Base object for managing results - 3D version."""

    def __init__(self, aperiodic_mode, periodic_mode, debug=False, verbose=True):
        """Initialize BaseResults3D object."""

        BaseResults2DT.__init__(self, aperiodic_mode, periodic_mode, debug=debug, verbose=verbose)

        self._reset_event_results()


    def __len__(self):
        """Redefine the length of the objects as the number of event results."""

        return len(self.event_group_results)


    def __getitem__(self, ind):
        """Allow for indexing into the object to select fit results for a specific event."""

        return get_results_by_row(self.event_time_results, ind)


    def _reset_event_results(self, length=0):
        """Set, or reset, event results to be empty."""

        self.event_group_results = [[]] * length
        self.event_time_results = {}


    @property
    def has_model(self):
        """Redefine has_model marker to reflect the event results."""

        return bool(self.event_group_results)


    @property
    def n_peaks_(self):
        """How many peaks were fit for each model, for each event."""

        return np.array([[res.peak_params.shape[0] for res in gres] \
            if self.has_model else None for gres in self.event_group_results])


    def drop(self, drop_inds=None, window_inds=None):
        """Drop one or more model fit results from the object.

        Parameters
        ----------
        drop_inds : dict or int or array_like of int or array_like of bool
            Indices to drop model fit results for.
            If not dict, specifies the event indices, with time windows specified by `window_inds`.
            If dict, each key reflects an event index, with corresponding time windows to drop.
        window_inds : int or array_like of int or array_like of bool
            Indices of time windows to drop model fits for (applied across all events).
            Only used if `drop_inds` is not a dictionary.

        Notes
        -----
        This method sets the model fits as null, and preserves the shape of the model fits.
        """

        # Local import - avoid circular
        from specparam import SpectralModel

        null_model = SpectralModel(**self.get_settings()._asdict()).get_results()

        drop_inds = drop_inds if isinstance(drop_inds, dict) else \
            dict(zip(check_inds(drop_inds), repeat(window_inds)))

        for eind, winds in drop_inds.items():

            winds = check_inds(winds)
            for wind in winds:
                self.event_group_results[eind][wind] = null_model
            for key in self.event_time_results:
                self.event_time_results[key][eind, winds] = np.nan


    def add_results(self, results, append=False):
        """Add results data into object.

        Parameters
        ----------
        results : list of FitResults or list of list of FitResults
            List of data objects containing results from fitting power spectrum models.
        append : bool, optional, default: False
            Whether to append results to event_group_results.
        """

        if append:
            self.event_group_results.append(results)
        else:
            self.event_group_results = results


    def get_results(self):
        """Return the results from across the set of events."""

        return self.event_time_results


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
        out : list of ndarray
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

        return [get_group_params(gres, name, col) for gres in self.event_group_results]


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
        einds = check_inds(event_inds, self.n_events)
        winds = check_inds(window_inds, self.n_time_windows)

        if output_type == 'event':

            # Initialize a new model object, with same settings as current object
            output = SpectralTimeEventModel(**self.get_settings()._asdict(), verbose=self.verbose)
            output.add_meta_data(self.get_meta_data())

            if event_inds is not None or window_inds is not None:

                # Add data for specified power spectra, if available
                if self.has_data:
                    output.spectrograms = self.spectrograms[einds, :, :][:, :, winds]

                # Add results for specified power spectra - event group results
                temp = [self.event_group_results[ei][wi] for ei in einds for wi in winds]
                step = int(len(temp) / len(einds))
                output.event_group_results = \
                    [temp[ind:ind+step] for ind in range(0, len(temp), step)]

                # Add results for specified power spectra - event time results
                output.event_time_results = \
                    {key : self.event_time_results[key][event_inds][:, window_inds] \
                    for key in self.event_time_results}

        elif output_type in ['time', 'group']:

            if event_inds is not None or window_inds is not None:

                # Move specified results & data to `group_results` & `power_spectra` for export
                self.group_results = \
                    [self.event_group_results[ei][wi] for ei in einds for wi in winds]
                if self.has_data:
                    self.power_spectra = np.hstack(self.spectrograms[einds, :, :][:, :, winds]).T

            new_inds = range(0, len(self.group_results)) if self.group_results else None
            output = super().get_group(new_inds, output_type)

            self._reset_group_results()
            self._reset_data_results(clear_spectra=True)

        return output


    def convert_results(self, peak_org):
        """Convert the event results to be organized across events and time windows.

        Parameters
        ----------
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        self.event_time_results = event_group_to_dict(self.event_group_results, peak_org)
