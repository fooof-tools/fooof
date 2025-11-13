"""Metrics object."""

from copy import deepcopy

import numpy as np

from specparam.metrics.metric import Metric
from specparam.metrics.definitions import METRICS, check_metric_definition
from specparam.reports.strings import gen_metrics_str

###################################################################################################
###################################################################################################

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

        metric = check_metric_definition(metric, METRICS)

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


    def get_metrics(self, category, measure=None):
        """Get requested metric(s) from the object.

        Parameters
        ----------
        category : str
            Category of metric to extract, e.g. 'error' or 'gof'.
            If 'all', returns all available metrics.
        measure : str, optional
            Name of the specific measure(s) to return.

        Returns
        -------
        metrics : dict
            Dictionary of requested metrics.
        """

        if category == 'all':
            out = self.results

        else:

            out = {ke : va for ke, va in self.results.items() if category in ke}

            if measure is not None:
                out = {ke : va for ke, va in out.items() if measure in ke}

        out = np.array(list(out.values()))
        out = out[0] if out.size == 1 else out

        return out


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
    def categories(self):
        """Define alias for metric categories of all currently defined metrics."""

        return [metric.category for metric in self.metrics]


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


    def print(self, description=False, concise=False):
        """Print out the current metrics.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current metrics.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_metrics_str(self, description, concise))


    def reset(self):
        """Reset all metric results."""

        for metric in self.metrics:
            metric.reset()
