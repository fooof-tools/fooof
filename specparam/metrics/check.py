"""Functionality to check available metrics."""

###################################################################################################
###################################################################################################

def check_metrics():
    """Check the set of available metrics."""

    from specparam.metrics.definitions import METRICS

    print('Available metrics:')
    for metric in METRICS.values():
        print('    {:8s} {:12s} : {:s}'.format(\
            metric.category, metric.measure, metric.description))
