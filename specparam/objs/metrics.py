"""Metrics object."""

from copy import deepcopy

import numpy as np

###################################################################################################
###################################################################################################

class Metric():
    """Define a metric to apply to a power spectrum model.

    Parameters
    ----------
    type : str
        The type of measure, e.g. 'error' or 'gof'.
    measure : str
        The specific measure, e.g. 'r_squared'.
    func : callable
        The function that computes the metric.
    kwargs : dictionary
        Additional keyword argument to compute the metric.
        Each key should be the name of the additional argument.
        Each value should be a lambda function that takes 'data' & 'results'
        and returns the desired parameter / computed value.
    """

    def __init__(self, type, measure, func, kwargs=None):
        """Initialize metric."""

        self.type = type
        self.measure = measure
        self.func = func
        self.result = np.nan
        self.kwargs = {} if not kwargs else kwargs


    def __repr__(self):
        """Set string representation of object."""

        return 'Metric: ' + self.label


    @property
    def label(self):
        """Define label property."""

        return self.type + '_' + self.measure


    @property
    def flabel(self):
        """Define formatted label property."""

        if self.type == 'error':
            flabel = '{} ({})'.format(self.type.capitalize(), self.measure.upper())
        if self.type == 'gof':
            flabel = '{} ({})'.format(self.type.upper(), self.measure)

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

        self.result = self.func(data.power_spectrum, results.model.modeled_spectrum_, **kwargs)


class Metrics():
    """Define a collection of metrics.

    Parameters
    ----------
    metrics : list of Metric or list of dict
        Metric(s) to add to the object.
    """

    def __init__(self, metrics=None):
        """Initialize metrics."""

        self.metrics = []
        if metrics:
            self.add_metrics(metrics)


    def __len__(self):
        """Define length of the object as the number of metrics."""

        return len(self.labels)


    def __getitem__(self, label):
        """Index into the object based on metric label.

        Parameters
        ----------
        label : str
            Label of the metric to access.
        """

        for ind, clabel in enumerate(self.labels):
            if label == clabel:
                return self.metrics[ind]

        raise ValueError('Requested label not found.')


    def add_metric(self, metric):
        """Add a metric to the object.

        Parameters
        ----------
        metric : Metric or dict
            Metric to add to the object.
            If dict, should have keys corresponding to a metric definition.
        """

        if isinstance(metric, dict):
            metric = Metric(**metric)

        self.metrics.append(deepcopy(metric))


    def add_metrics(self, metrics):
        """Add metric(s) to object

        Parameters
        ----------
        metrics : list of Metric or list of dict
            Metric(s) to add to the object.
        """

        for metric in metrics:
            self.add_metric(metric)


    def compute_metrics(self, data, results):
        """Compute all currently defined metrics.

        Parameters
        ----------
        data : Data
            Model data.
        results : Results
            Model results.
        """

        for metric in self.metrics:
            metric.compute_metric(data, results)


    @property
    def types(self):
        """Define alias for metric type of all currently defined metrics."""

        return [metric.type for metric in self.metrics]


    @property
    def measures(self):
        """Define alias for measure description of all currently defined metrics."""

        return [metric.measure for metric in self.metrics]


    @property
    def labels(self):
        """Define alias for labels of all currently defined metrics."""

        return [metric.label for metric in self.metrics]


    @property
    def flabels(self):
        """Define alias for formatted labels of all currently defined metrics."""

        return [metric.flabel for metric in self.metrics]


    @property
    def results(self):
        """Define alias for ouputs of all currently defined metrics."""

        return {metric.label : metric.result for metric in self.metrics}


    def add_results(self, results):
        """Add computed metric results.

        Parameters
        ----------
        results : dict
            Metric results.
            Keys should match metric labels, with each value being a metric result.
        """

        for key, value in results.items():
            self[key].result = value
