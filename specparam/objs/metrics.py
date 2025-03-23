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

        return self.measure + '-' + self.metric


    def compute_metric(self, data, results):
        """Compute metric.

        Parameters
        ----------
        data : Data
            Model data.
        results : Results
            Model results.
        """

        self.output = self.func(data.power_spectrum, results.modeled_spectrum_)


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
    def outputs(self):
        """Define alias for ouputs of all currently defined metrics."""

        return {metric.label : metric.output for metric in self.metrics}


    # TEMP: CHECK IF THIS IS HOW TO MANAGE THIS
    def set_defaults(self):
        """Set default metrics."""

        from specparam.measures.error import compute_mean_abs_error
        from specparam.measures.gof import compute_r_squared

        self.add_metrics([Metric('error', 'mae', compute_mean_abs_error),
                          Metric('gof', 'r_squared', compute_r_squared)])
