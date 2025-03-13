"""Classes & functions for managing parameters for simulating power spectra."""

import numpy as np

from specparam.utils.select import groupby
from specparam.utils.checks import check_flat
from specparam.core.info import get_indices
from specparam.core.funcs import infer_ap_func
from specparam.modutils.errors import InconsistentDataError

from specparam.data import SimParams

###################################################################################################
###################################################################################################

def collect_sim_params(aperiodic_params, periodic_params, nlv):
    """Collect simulation parameters into a SimParams object.

    Parameters
    ----------
    aperiodic_params : list of float
        Parameters of the aperiodic component of the power spectrum.
    periodic_params : list of float or list of list of float
        Parameters of the periodic component of the power spectrum.
    nlv : float
        Noise level of the power spectrum.

    Returns
    -------
    SimParams
        Object containing the simulation parameters.
    """

    return SimParams(aperiodic_params.copy(),
                     sorted(groupby(check_flat(periodic_params), 3)),
                     nlv)


def update_sim_ap_params(sim_params, delta, field=None):
    """Update the aperiodic parameter definition in a SimParams object.

    Parameters
    ----------
    sim_params : SimParams
        Object storing the current parameter definition.
    delta : float or list of float
        Value(s) by which to update the parameters.
    field : {'offset', 'knee', 'exponent'} or list of string
        Field of the aperiodic parameter(s) to update.

    Returns
    -------
    new_sim_params : SimParams
        Updated object storing the new parameter definition.

    Raises
    ------
    InconsistentDataError
        If the input parameters and update values are inconsistent.
    """

    # Grab the aperiodic parameters that need updating
    ap_params = sim_params.aperiodic_params.copy()

    # If field isn't specified, check shapes line up and update across parameters
    if not field:
        if not len(ap_params) == len(delta):
            raise InconsistentDataError("The number of items to update and "
                                        "number of new values is inconsistent.")
        ap_params = [param + update for param, update in zip(ap_params, delta)]

    # If labels are given, update deltas according to their labels
    else:
        # This loop checks & casts to list, to work for single or multiple passed in values
        for cur_field, cur_delta in zip(list([field]) if not isinstance(field, list) else field,
                                        list([delta]) if not isinstance(delta, list) else delta):
            data_ind = get_indices(infer_ap_func(ap_params))[cur_field]
            ap_params[data_ind] = ap_params[data_ind] + cur_delta

    # Replace parameters. Note that this copies a new object, as data objects are immutable
    new_sim_params = sim_params._replace(aperiodic_params=ap_params)

    return new_sim_params


class Stepper():
    """Object for stepping across parameter values.

    Parameters
    ----------
    start : float
        Start value to iterate from.
    stop : float
        End value to iterate to.
    step : float
        Increment of each iteration.

    Attributes
    ----------
    len : int
        Length of generator range.
    data : iterator
        Set of specified parameters to iterate across.

    Examples
    --------
    Define a stepper object for center frequency values for an alpha peak:

    >>> alpha_cf_steps = Stepper(8, 12.5, 0.5)
    """

    def __init__(self, start, stop, step):
        """Initialize a Stepper object."""

        self._check_values(start, stop, step)

        self.start = start
        self.stop = stop
        self.step = step
        self.len = round((stop-start)/step)
        self.data = iter(np.arange(start, stop, step))

    def __len__(self):

        return self.len

    def __next__(self):

        return round(next(self.data), 4)

    def __iter__(self):

        return self.data

    @staticmethod
    def _check_values(start, stop, step):
        """Checks if provided values are valid.

        Parameters
        ----------
        start, stop, step : float
            Definition of the parameter range to iterate over.

        Raises
        ------
        ValueError
            If the given values for defining the iteration range are inconsistent.
        """

        if any(ii < 0 for ii in [start, stop]):
            raise ValueError("Inputs 'start' and 'stop' should be positive values.")

        if (stop - start) * step < 0:
            raise ValueError("The sign of 'step' does not align with 'start' / 'stop' values.")

        if start == stop:
            raise ValueError("Input 'start' and 'stop' must be different values.")

        if not abs(step) < abs(stop - start):
            raise ValueError("Input 'step' is too large given values for 'start' and 'stop'.")


def param_iter(params):
    """Create a generator to iterate across parameter ranges.

    Parameters
    ----------
    params : list of floats and Stepper
        Parameters over which to iterate, including a Stepper object.
        The Stepper defines the iterated parameter and its range.
        Floats define the other parameters, that will be held constant.

    Yields
    ------
    list of floats
        Next generated list of parameters.

    Raises
    ------
    ValueError
        If the number of Stepper objects given is greater than one.

    Examples
    --------
    Iterate across exponent values from 1 to 2, in steps of 0.1:

    >>> aps = param_iter([Stepper(1, 2, 0.1), 1])

    Iterate over center frequency values from 8 to 12 in increments of 0.25:

    >>> peaks = param_iter([Stepper(8, 12, .25), 0.5, 1])
    """

    # If input is a list of lists, check each element, and flatten if needed
    if isinstance(params[0], list):
        params = [item for sublist in params for item in sublist]

    # Finds where Stepper object is. If there is more than one, raise an error
    iter_ind = 0
    num_iters = 0
    for cur_ind, param in enumerate(params):

        if isinstance(param, Stepper):
            num_iters += 1
            iter_ind = cur_ind

        if num_iters > 1:
            raise ValueError("Iteration is only supported across one parameter at a time.")

    # Generate and yield next set of parameters
    gen = params[iter_ind]
    while True:
        try:
            params[iter_ind] = next(gen)
            yield params
        except StopIteration:
            return


def param_sampler(params, probs=None):
    """Create a generator to sample randomly from possible parameters.

    Parameters
    ----------
    params : list of lists or list of float
        Possible parameter values.
    probs : list of float, optional
        Probabilities with which to sample each parameter option.
        If None, each parameter option is sampled uniformly.

    Yields
    ------
    list of float
        A randomly sampled set of parameters.

    Examples
    --------
    Sample from aperiodic definitions with high and low exponents, with 50% probability of each:

    >>> aps = param_sampler([[1, 1], [2, 1]], probs=[0.5, 0.5])

    Sample from peak definitions of alpha or alpha & beta, with 75% change of sampling just alpha:

    >>> peaks = param_sampler([[10, 1, 1], [[10, 1, 1], [20, 0.5, 1]]], probs=[0.75, 0.25])
    """

    # If input is a list of lists, check each element, and flatten if needed
    if isinstance(params[0], list):
        params = [check_flat(lst) for lst in params]

    # In order to use numpy's choice, with probabilities, choices are made on indices
    # This is because the params can be a messy-sized list, that numpy choice does not like
    inds = np.array(range(len(params)))

    # Check that length of options is same as length of probs, if provided
    if np.any(probs):
        if len(inds) != len(probs):
            raise ValueError("The number of options must match the number of probabilities.")

    # While loop allows the generator to be called an arbitrary number of times
    while True:
        yield params[np.random.choice(inds, p=probs)]


def param_jitter(params, jitters):
    """Create a generator that adds jitter to parameter definitions.

    Parameters
    ----------
    params : list of lists or list of float
        Possible parameter values.
    jitters : list of lists or list of float
        The scale of the jitter for each parameter.
        Must be the same shape and organization as `params`.

    Yields
    ------
    list of float
        A jittered set of parameters.

    Notes
    -----
    - Jitter is added as random samples from a normal (gaussian) distribution.

        - The jitter specified corresponds to the standard deviation of the normal distribution.
    - For any parameter for which there should be no jitter, set the corresponding value to zero.

    Examples
    --------
    Jitter aperiodic definitions, for offset and exponent, each with the same amount of jitter:

    >>> aps = param_jitter([1, 1], [0.1, 0.1])

    Jitter center frequency of peak definitions, by different amounts for alpha & beta:

    >>> peaks = param_jitter([[10, 1, 1], [20, 1, 1]], [[0.1, 0, 0], [0.5, 0, 0]])
    """

    # Check if inputs are list of lists, and flatten if so
    if isinstance(params[0], list):
        params = check_flat(params)
        jitters = check_flat(jitters)

    # While loop allows the generator to be called an arbitrary number of times
    while True:

        out_params = [None] * len(params)
        for ind, (param, jitter) in enumerate(zip(params, jitters)):
            out_params[ind] = param + np.random.normal(0, jitter)

        yield out_params
