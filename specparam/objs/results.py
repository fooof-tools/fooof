"""Define base results objects."""

from copy import deepcopy
from itertools import repeat

import numpy as np

from specparam.bands.bands import check_bands
from specparam.objs.metrics import Metrics
from specparam.measures.metrics import METRICS
from specparam.utils.array import unlog
from specparam.utils.checks import check_inds, check_array_dim
from specparam.modutils.errors import NoModelError
from specparam.modutils.docs import docs_get_section, replace_docstring_sections
from specparam.data.data import FitResults
from specparam.data.conversions import group_to_dict, event_group_to_dict
from specparam.data.utils import (get_model_params, get_group_params,
                                  get_results_by_ind, get_results_by_row)
from specparam.sim.gen import gen_model

###################################################################################################
###################################################################################################

# Define set of results fields & default metrics to use
RESULTS_FIELDS = ['aperiodic_params_', 'gaussian_params_', 'peak_params_']
DEFAULT_METRICS = ['error_mae', 'gof_rsquared']


class ModelComponents():
    """Object for managing model components.

    Attributes
    ----------
    modeled_spectrum : 1d array
        Modeled spectrum.
    _spectrum_flat : 1d array
        Data attribute: flattened power spectrum, with the aperiodic component removed.
    _spectrum_peak_rm : 1d array
        Data attribute: power spectrum, with peaks removed.
    _ap_fit : 1d array
        Model attribute: values of the isolated aperiodic fit.
    _peak_fit : 1d array
        Model attribute: values of the isolated peak fit.
    """

    def __init__(self):
        """Initialize ModelComponents object."""

        self.reset()


    def reset(self):
        """Reset model components attributes."""

        # Data components
        self._spectrum_flat = None
        self._spectrum_peak_rm = None

        # Full model
        self.modeled_spectrum_ = None

        # Model components
        self._ap_fit = None
        self._peak_fit = None


    def get_component(self, component='full', space='log'):
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

        if self.modeled_spectrum_ is None:
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


class Results():
    """Object for managing results - base / 1D version.

    Parameters
    ----------
    modes : Modes
        Modes object with fit mode definitions.
    metrics : Metrics
        Metrics object with metric definitions.
    bands : bands
        Bands object with band definitions.
    """
    # pylint: disable=attribute-defined-outside-init, arguments-differ

    def __init__(self, modes=None, metrics=None, bands=None):
        """Initialize Results object."""

        self.modes = modes

        self.add_bands(bands)
        self.add_metrics(metrics)

        self.model = ModelComponents()

        # Initialize results attributes
        self._reset_results(True)
        self._fields = RESULTS_FIELDS


    @property
    def has_model(self):
        """Indicator for if the object contains a model fit.

        Notes
        -----
        This check uses the aperiodic params, which are:

        - nan if no model has been fit
        - necessarily defined, as floats, if model has been fit
        """

        return not np.all(np.isnan(self.aperiodic_params_))


    @property
    def n_peaks_(self):
        """How many peaks were fit in the model."""

        n_peaks = None
        if self.has_model:
            n_peaks = self.peak_params_.shape[0]

        return n_peaks


    @property
    def n_params_(self):
        """The total number of parameters fit in the model."""

        n_params = None
        if self.has_model:
            n_peak_params = self.modes.periodic.n_params * self.n_peaks_
            n_params = n_peak_params + self.modes.aperiodic.n_params

        return n_params


    def add_bands(self, bands):
        """Add bands definition to object.

        Parameters
        ----------
        bands : Bands or dict or int or None
            How to organize peaks into bands.
            If Bands, defines band ranges, if int, specifies a number of bands to consider.
            If dict, should be a set of band definitions to be converted into a Bands object.
            If None, sets bands as an empty Bands object.
        """

        self.bands = deepcopy(check_bands(bands))


    def add_metrics(self, metrics):
        """Add metrics definition to object.

        Parameters
        ----------
        metrics : Metrics or list of Metric or list or str
            Metrics definition(s) to add to object.
        """

        if isinstance(metrics, Metrics):
            self.metrics = deepcopy(metrics)
        elif isinstance(metrics, list):
            self.metrics = Metrics(\
                [METRICS[metric] if isinstance(metric, str) else metric for metric in metrics])
        else:
            self.metrics = Metrics([METRICS[metric] for metric in DEFAULT_METRICS])


    def add_results(self, results):
        """Add results data into object from a FitResults object.

        Parameters
        ----------
        results : FitResults
            A data object containing the results from fitting a power spectrum model.
        """

        # Add parameter fields and then select and add metrics results
        for pfield in self._fields:
            setattr(self, pfield, getattr(results, pfield.strip('_')))

        self.metrics.add_results(results.metrics)

        self._check_loaded_results(results._asdict())


    def get_results(self):
        """Return model fit parameters and goodness of fit metrics.

        Returns
        -------
        FitResults
            Object containing the model fit results from the current object.
        """

        results = FitResults(
            **{key.strip('_') : getattr(self, key) for key in self._fields},
            metrics=self.metrics.results)

        return results


    def get_params(self, name, field=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract.
        field : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
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

        return get_model_params(self.get_results(), self.modes, name, field)


    def _check_loaded_results(self, data):
        """Check if results have been added and check data.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # If results loaded, check dimensions of peak parameters
        #   This fixes an issue where they end up the wrong shape if they are empty (no peaks)
        if set(self._fields).issubset(set(data.keys())):
            self.peak_params_ = check_array_dim(self.peak_params_)
            self.gaussian_params_ = check_array_dim(self.gaussian_params_)


    def _reset_results(self, clear_results=False):
        """Set, or reset, results attributes to empty.

        Parameters
        ----------
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        if clear_results:

            # Aperiodic parameters
            if self.modes:
                self.aperiodic_params_ = np.array([np.nan] * self.modes.aperiodic.n_params)
            else:
                self.aperiodic_params_ = np.nan

            # Periodic parameters
            if self.modes:
                self.gaussian_params_ = np.empty([0, self.modes.periodic.n_params])
                self.peak_params_ = np.empty([0, self.modes.periodic.n_params])
            else:
                self.gaussian_params_ = np.nan
                self.peak_params_ = np.nan

            # Reset model components
            self.model.reset()


    def _regenerate_model(self, freqs):
        """Regenerate model fit from parameters.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear scale.
        """

        self.model.modeled_spectrum_, self.model._peak_fit, self.model._ap_fit = \
            gen_model(freqs, self.modes.aperiodic, self.aperiodic_params_,
                      self.modes.periodic, self.gaussian_params_, return_components=True)


@replace_docstring_sections([docs_get_section(Results.__doc__, 'Parameters')])
class Results2D(Results):
    """Object for managing results - 2D version.

    Parameters
    ----------
    % copied in from Results
    """

    def __init__(self, modes=None, metrics=None, bands=None):
        """Initialize Results2D object."""

        Results.__init__(self, modes=modes, metrics=metrics, bands=bands)

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

        return bool(self.group_results)


    @property
    def n_peaks_(self):
        """How many peaks were fit for each model."""

        n_peaks = None
        if self.has_model:
            n_peaks = np.array([res.peak_params.shape[0] for res in self])

        return n_peaks


    @property
    def n_null_(self):
        """How many model fits are null."""

        n_null = None
        if self.has_model:
            n_null = sum([1 for res in self.group_results if np.isnan(res.aperiodic_params[0])])

        return n_null


    @property
    def null_inds_(self):
        """The indices for model fits that are null."""

        null_inds = None
        if self.has_model:
            null_inds = [ind for ind, res in enumerate(self.group_results) \
                if np.isnan(res.aperiodic_params[0])]

        return null_inds


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

        null_results = Results(self.modes, self.metrics.labels, self.bands).get_results()
        for ind in check_inds(inds):
            self.group_results[ind] = null_results


    def get_params(self, name, field=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract across the group.
        field : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
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
            If the input for the `field` input is not understood.

        Notes
        -----
        When extracting peak information ('peak_params' or 'gaussian_params'), an additional
        column is appended to the returned array, indicating the index that the peak came from.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")

        return get_group_params(self.group_results, self.modes, name, field)


@replace_docstring_sections([docs_get_section(Results.__doc__, 'Parameters')])
class Results2DT(Results2D):
    """Object for managing results - 2D transpose version.

    Parameters
    ----------
    % copied in from Results
    """

    def __init__(self, modes=None, metrics=None, bands=None):
        """Initialize Results2DT object."""

        Results2D.__init__(self, modes=modes, metrics=metrics, bands=bands)

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


    def convert_results(self):
        """Convert the model results to be organized across time windows."""

        self.time_results = group_to_dict(self.group_results, self.modes, self.bands)


@replace_docstring_sections([docs_get_section(Results.__doc__, 'Parameters')])
class Results3D(Results2DT):
    """Object for managing results - 3D version.

    Parameters
    ----------
    % copied in from Results
    """

    def __init__(self, modes=None, metrics=None, bands=None):
        """Initialize Results3D object."""

        Results2DT.__init__(self, modes=modes, metrics=metrics, bands=bands)

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

        n_peaks = None
        if self.has_model:
            n_peaks = np.array([[res.peak_params.shape[0] for res in gres] \
                for gres in self.event_group_results])

        return n_peaks


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

        null_results = Results(self.modes, self.metrics.labels, self.bands).get_results()

        drop_inds = drop_inds if isinstance(drop_inds, dict) else \
            dict(zip(check_inds(drop_inds), repeat(window_inds)))

        for eind, winds in drop_inds.items():

            winds = check_inds(winds)
            for wind in winds:
                self.event_group_results[eind][wind] = null_results
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


    def get_params(self, name, field=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        name : {'aperiodic_params', 'peak_params', 'gaussian_params', 'error', 'r_squared'}
            Name of the data field to extract across the group.
        field : {'CF', 'PW', 'BW', 'offset', 'knee', 'exponent'} or int, optional
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
            If the input for the `field` input is not understood.

        Notes
        -----
        When extracting peak information ('peak_params' or 'gaussian_params'), an additional
        column is appended to the returned array, indicating the index that the peak came from.
        """

        return [get_group_params(gres, self.modes, name, field) for gres in self.event_group_results]


    def convert_results(self):
        """Convert the event results to be organized across events and time windows."""

        self.event_time_results = event_group_to_dict(\
            self.event_group_results, self.modes, self.bands)
