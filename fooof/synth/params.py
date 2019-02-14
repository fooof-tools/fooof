"""Classes & functions for managing parameter choices for synthesizing power spectra."""

from collections import namedtuple

import numpy as np

from fooof.core.utils import check_flat

###################################################################################################
###################################################################################################

SynParams = namedtuple('SynParams', ['aperiodic_params', 'gaussian_params', 'nlv'])

SynParams.__doc__ = """\
Stores parameters used to synthesize a single power spectra.

Attributes
----------
aperiodic_params : 1d array, len 2 or 3
    Parameters that define the aperiodic fit. As [Intercept, (Knee), Exponent].
        The knee parameter is only included if aperiodic is fit with knee. Otherwise, length is 2.
gaussian_params : 2d array, shape=[n_peaks, 3]
    Fitted parameter values for the peaks. Each row is a peak, as [CF, Amp, BW].
nlv : float
    Noise level added to the generated power spectrum.
"""

class Stepper():
    """Object for stepping across parameter values.

    Parameters
    ----------
    start : float
        Start value to iterate from.
    stop : float
        End value to iterate to.
    step : float
        Incremet of each iteration.

    Attributes
    ----------
    len : int
        Length of generator range.
    data : iterator
        Set of specified parameters to iterate across.
    """

    def __init__(self, start, stop, step):

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
        """Checks if provided values are valid for use."""

        if any(i < 0 for i in [start, stop, step]):
            raise ValueError("'start', 'stop', and 'step' should all be positive values")

        if not start < stop:
            raise ValueError("'start' should be less than stop")

        if not step < (stop - start):
            raise ValueError("'step' is too large given 'start' and 'stop' values")


def param_iter(params):
    """Generates parameters to iterate over.

    Parameters
    ----------
    params : list of floats and Stepper
        Parameters over which to iterate in which the
        Stepper object defines iterated parameter and its range and,
        floats are other parameters that will be held constant.

    Yields
    ------
    list of floats
        Next generated list of parameters.

    Examples
    --------
    Iterates over center frequency values from 8 to 12 in increments of .25.

    >>> osc = param_iter([Stepper(8, 12, .25), 1, 1])
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
            raise ValueError("Iteration is only supported on one parameter")

    # Generate and yield next set of parameters
    gen = params[iter_ind]
    while True:
        try:
            params[iter_ind] = next(gen)
            yield params
        except StopIteration:
            return


def param_sampler(params, probs=None):
    """Makes a generator to sample randomly from possible parameters.

    Parameters
    ----------
    params : list of lists or list of float
        Possible parameter values.
    probs : list of float, optional
        Probabilities with which to sample each parameter option.
        If None, each parameter option is sampled uniformly.

    Yields
    ------
    obj
        A randomly sampled element from params.
    """

    # If input is a list of lists, check each element, and flatten if needed
    if isinstance(params[0], list):
        params = [check_flat(lst) for lst in params]

    # In order to use numpy's choice, with probabilities, choices are made on indices
    # This is because the params can be a messy-sized list, that numpy choice does not like
    inds = np.array(range(len(params)))

    # While loop allows the generator to be called an arbitrary number of times.
    while True:
        yield params[np.random.choice(inds, p=probs)]
