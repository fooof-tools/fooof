"""Define results objects."""

from copy import deepcopy
from itertools import repeat

import numpy as np

from specparam.bands.bands import check_bands
from specparam.modes.modes import Modes
from specparam.results.params import ModelParameters
from specparam.results.components import ModelComponents
from specparam.metrics.metrics import Metrics
from specparam.utils.checks import check_inds
from specparam.modutils.errors import NoModelError
from specparam.modutils.docs import (copy_doc_func_to_method, docs_get_section,
                                     replace_docstring_sections)
from specparam.data.stores import FitResults
from specparam.data.conversions import group_to_dict, event_group_to_dict
from specparam.data.utils import (get_group_params, get_group_metrics,
                                  get_results_by_ind, get_results_by_row)
from specparam.sim.gen import gen_model

###################################################################################################
###################################################################################################

# Define set of results fields & default metrics to use
DEFAULT_METRICS = ['error_mae', 'gof_rsquared']


class Results():
    """Object for managing results - base / 1D version.

    Parameters
    ----------
    modes : Modes
        Modes object with fit mode definitions.
    metrics : Metrics
        Metrics object with metric definitions.
    bands : Bands or dict or int or None
        Bands object with band definitions, or definition that can be turned into a Bands object.

    Attributes
    ----------
    modes : Modes
        Modes object with fit mode definitions.
    bands : Bands
        Bands object with band definitions.
    model : ModelComponents
        Manages the model fit and components.
    params : ModelParameters
        Manages the model fit parameters.
    metrics : Metrics
        Metrics object with metric definitions.
    """
    # pylint: disable=attribute-defined-outside-init, arguments-differ

    def __init__(self, modes=None, metrics=None, bands=None):
        """Initialize Results object."""

        self.modes = modes if modes else Modes(None, None)

        self.add_bands(bands)
        self.add_metrics(metrics)

        self.model = ModelComponents()
        self.params = ModelParameters(modes=modes)

        # Initialize results attributes
        self._reset_results(True)


    @property
    def has_model(self):
        """Indicator for if the object contains a model fit.

        Notes
        -----
        This checks the aperiodic params, which are necessarily defined if a model has been fit.
        """

        return self.params.aperiodic.has_params


    @property
    def n_peaks(self):
        """How many peaks were fit in the model."""

        n_peaks = None
        if self.has_model:
            n_peaks = self.params.periodic.params.shape[0]

        return n_peaks


    @property
    def n_params(self):
        """The total number of parameters fit in the model."""

        n_params = None
        if self.has_model:
            n_peak_params = self.modes.periodic.n_params * self.n_peaks
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
        metrics : Metrics or list of Metric or list of str or None
            Metrics definition(s) to add to object.
            If None, initialized with default metrics.
        """

        if metrics is None:
            metrics = DEFAULT_METRICS

        if isinstance(metrics, Metrics):
            self.metrics = deepcopy(metrics)
        else:
            self.metrics = Metrics(metrics)


    def add_results(self, results):
        """Add results data into object from a FitResults object.

        Parameters
        ----------
        results : FitResults
            A data object containing the results from fitting a power spectrum model.
        """

        # TODO: use check_array_dim for peak arrays? Or is / should this be done in `add_params`

        for component in self.modes.components:
            for version in ['fit', 'converted']:
                attr_comp = 'peak' if component == 'periodic' else component
                getattr(self.params, component).add_params(\
                    version, getattr(results, attr_comp + '_' + version))

        self.metrics.add_results(results.metrics)


    def get_results(self):
        """Return model fit parameters and metrics.

        Returns
        -------
        FitResults
            Object containing the model fit results from the current object.
        """

        return FitResults(**self.params.asdict(), metrics=self.metrics.results)


    def get_params(self, component, field=None, version=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        component : {'aperiodic', 'periodic'}
            Name of the component to extract parameters for.
        field : str or int, optional
            Column name / index to extract from selected data, if requested.
            If str, should align with a parameter label for the component fit mode.
        version : {'fit', 'converted'}
            Which version of the parameters to extract.

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
        If there are no fit peaks (no periodic parameters), this method will return NaN.
        """

        component = 'periodic' if component == 'peak' else component

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")

        return getattr(self.params, component).get_params(version, field)


    @copy_doc_func_to_method(Metrics.get_metrics)
    def get_metrics(self, category, measure=None):

        return self.metrics.get_metrics(category, measure)


    def _reset_results(self, clear_results=False):
        """Set, or reset, results attributes to empty.

        Parameters
        ----------
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        if clear_results:
            self.params.reset()
            self.model.reset()
            self.metrics.reset()


    def _regenerate_model(self, freqs):
        """Regenerate model fit from parameters.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear scale.
        """

        self.model.modeled_spectrum, self.model._peak_fit, self.model._ap_fit = \
            gen_model(freqs, self.modes.aperiodic, self.params.aperiodic.get_params('fit'),
                      self.modes.periodic, self.params.periodic.get_params('fit'),
                      return_components=True)


@replace_docstring_sections([docs_get_section(Results.__doc__, 'Parameters'),
                             docs_get_section(Results.__doc__, 'Attributes')])
class Results2D(Results):
    """Object for managing results - 2D version.

    Parameters
    ----------
    % copied in from Results

    Attributes
    ----------
    % copied in from Results
    group_results : list of FitResults
        Results of the model fit for each power spectrum.
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
    def n_peaks(self):
        """How many peaks were fit for each model."""

        n_peaks = None
        if self.has_model:
            n_peaks = np.array([res.peak_fit.shape[0] for res in self])

        return n_peaks


    @property
    def n_null(self):
        """How many model fits are null."""

        n_null = None
        if self.has_model:
            n_null = sum([1 for res in self.group_results if np.isnan(res.aperiodic_fit[0])])

        return n_null


    @property
    def null_inds(self):
        """The indices for model fits that are null."""

        null_inds = None
        if self.has_model:
            null_inds = [ind for ind, res in enumerate(self.group_results) \
                if np.isnan(res.aperiodic_fit[0])]

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


    def get_params(self, component, field=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        component : {'aperiodic', 'periodic'}
            Name of the component to extract parameters for.
        field : str or int, optional
            Column name / index to extract from selected data, if requested.
            If str, should align with a parameter label for the component fit mode.

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
        When extracting peak parameters, an additional column is appended to the
        returned array, indicating the index that the peak came from.
        """

        if not self.has_model:
            raise NoModelError("No model fit results are available, can not proceed.")

        return get_group_params(self.group_results, self.modes, component, field)


    @copy_doc_func_to_method(Metrics.get_metrics)
    def get_metrics(self, category, measure=None):

        return get_group_metrics(self.group_results, category, measure)


@replace_docstring_sections([docs_get_section(Results.__doc__, 'Parameters'),
                             docs_get_section(Results2D.__doc__, 'Attributes')])
class Results2DT(Results2D):
    """Object for managing results - 2D transpose version.

    Parameters
    ----------
    % copied in from Results

    Attributes
    ----------
    % copied in from Results2D
    time_results : dict
        Results of the model fit across each time window.
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


@replace_docstring_sections([docs_get_section(Results.__doc__, 'Parameters'),
                             docs_get_section(Results2DT.__doc__, 'Attributes')])
class Results3D(Results2DT):
    """Object for managing results - 3D version.

    Parameters
    ----------
    % copied in from Results

    Attributes
    ----------
    % copied in from Results2DT
    event_group_results : list of list of FitResults
        Full model results collected across all events and models.
    event_time_results : dict
        Results of the model fit across each time window, collected across events.
        Each value in the dictionary stores a model fit parameter, as [n_events, n_time_windows].
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
    def n_peaks(self):
        """How many peaks were fit for each model, for each event."""

        n_peaks = None
        if self.has_model:
            n_peaks = np.array([[res.peak_fit.shape[0] for res in gres] \
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


    def get_params(self, component, field=None):
        """Return model fit parameters for specified feature(s).

        Parameters
        ----------
        component : {'aperiodic', 'periodic'}
            Name of the component to extract parameters for.
        field : str or int, optional
            Column name / index to extract from selected data, if requested.
            If str, should align with a parameter label for the component fit mode.

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
        When extracting peak parameters, an additional column is appended to the
        returned array, indicating the index that the peak came from.
        """

        return [get_group_params(gres, self.modes, component, field) \
                    for gres in self.event_group_results]


    def convert_results(self):
        """Convert the event results to be organized across events and time windows."""

        self.event_time_results = event_group_to_dict(\
            self.event_group_results, self.modes, self.bands)
