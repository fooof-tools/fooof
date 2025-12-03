"""Metric object."""

import numpy as np

###################################################################################################
###################################################################################################

class Metric():
    """Define a metric to apply to a power spectrum model.

    Parameters
    ----------
    category : str
        The category of measure, e.g. 'error' or 'gof'.
    measure : str
        The specific measure, e.g. 'r_squared'.
    description : str
        Description of the metric.
    func : callable
        The function that computes the metric.
    kwargs : dictionary
        Additional keyword argument to compute the metric.
        Each key should be the name of the additional argument.
        Each value should be a lambda function that takes 'data' & 'results'
        and returns the desired parameter / computed value.
    """

    def __init__(self, category, measure, description, func, kwargs=None):
        """Initialize metric."""

        self.category = category
        self.measure = measure
        self.description = description
        self.func = func
        self.result = np.nan
        self.kwargs = {} if not kwargs else kwargs


    def __repr__(self):
        """Set string representation of object."""

        return 'Metric: ' + self.label


    @property
    def label(self):
        """Define label property."""

        return self.category + '_' + self.measure


    @property
    def flabel(self):
        """Define formatted label property."""

        if self.category == 'error':
            flabel = '{} ({})'.format(self.category.capitalize(), self.measure.upper())
        if self.category == 'gof':
            flabel = '{} ({})'.format(self.category.upper(), self.measure)

        return flabel


    def compute_metric(self, data, results):
        """Compute metric.

        Parameters
        ----------
        data : Data
            Model data.
        results : Results
            Model results.
        """

        kwargs = {}
        for key, lfunc in self.kwargs.items():
            kwargs[key] = lfunc(data, results)

        self.result = self.func(data.power_spectrum, results.model.modeled_spectrum, **kwargs)


    def reset(self):
        """Reset metric result."""

        self.result = np.nan
