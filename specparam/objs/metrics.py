"""Metrics object."""

from collections import namedtuple

###################################################################################################
###################################################################################################

class Metric():
    """Define a metric to apply to a power spectrum model.

    Parameters
    ----------
    measure : str
        The type of measure, e.g. 'error' or 'gof'.
    metric : str
        The specific measure, e.g. 'r_squared'.
    func : callable
        The function that computes the metric.
    kwargs : dictionary
        Additional keyword argument to compute the metric.
        Each key should be 'data' or 'results', specifying where to access the attribute from.
        Each value should be the name of the attribute to access and pass to compute the metric.
    """

    def __init__(self, measure, metric, func, kwargs=None):
        """Initialize metric."""

        self.measure = measure
        self.metric = metric
        self.func = func
        self.result = None
        self.kwargs = {} if not kwargs else kwargs


    def __repr__(self):
        """Set string representation of object."""

        return 'Metric: ' + self.label


    @property
    def label(self):
        """Define label property."""

        return self.measure + '_' + self.metric


    @property
    def flabel(self):
        """Define formatted label property."""

        label_els = self.label.split('_')

        if 'error' in self.label:
            flabel = '{} ({})'.format(label_els[0].capitalize(), label_els[1].upper())
        if 'gof' in self.label:
            flabel = '{} ({})'.format(label_els[0].upper(), label_els[1])

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

        # Select any specified additional keyword arguments from kwargs definition
        kwargs = {val.strip('_') : getattr({'results' : results, 'data' : data}[key], val) \
            for key, val in self.kwargs.items()}

        self.result = self.func(data.power_spectrum, results.modeled_spectrum_, **kwargs)


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

        self.metrics.append(metric)


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
