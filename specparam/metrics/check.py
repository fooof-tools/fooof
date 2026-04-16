"""Functionality to check available metrics."""

###################################################################################################
###################################################################################################

def check_metrics(category='all'):
    """Check the set of available metrics.

    Parameters
    ----------
    category : {'all', 'error', 'gof'}
        Which category of metrics to check.
    """

    from specparam.metrics.definitions import METRICS

    category = ['error', 'gof'] if category == 'all' else [category]

    for cat in category:
        print('Available {} metrics:'.format(cat))
        for metric in METRICS[cat].values():
            print('    {:15s}    {:s}'.format(metric.measure, metric.description))
