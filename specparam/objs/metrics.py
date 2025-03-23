"""Metrics object."""

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
    """

    def __init__(self, measure, metric, func):
        """Initialize metric."""

        self.measure = measure
        self.metric = metric
        self.func = func
        self.output = None


    def __repr__(self):
        """Set string representation of object."""

        return 'Metric: ' + self.label


    @property
    def label(self):
        """Define label property."""

        return self.measure + '_' + self.metric


    def compute_metric(self, data, results, **kwargs):
        """   """

        self.output = self.func(data.power_spectrum, results.modeled_spectrum_, **kwargs)


class Metrics():
    """Define a collection of metrics.

    Parameters
    ----------
    metrics : list of Metric or list of dict
        Metric(s) to add to the object.
    """

    def __init__(self, metrics):
        """Initialize metrics."""

        self.metrics = []
        for metric in metrics:
            self.add_metric(metric)


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
    def outputs(self):
        """Define alias for ouputs of all currently defined metrics."""

        return {metric.label : metric.output for metric in self.metrics}
