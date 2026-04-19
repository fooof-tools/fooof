"""Functionality to check available metrics."""

from specparam.reports.strings import gen_metric_str_lst, _format

###################################################################################################
###################################################################################################

def check_metrics(category='all', concise=False):
    """Check the set of available metrics.

    Parameters
    ----------
    category : {'all', 'error', 'gof'}
        Which category of metrics to check.
    """

    from specparam.metrics.definitions import METRICS

    categories = list(METRICS.keys()) if category == 'all' else [category]

    str_lst = []
    for category in categories:

        str_lst.extend(['', 'AVAILABLE {} METRICS'.format(category.upper()), ''])

        for metric in METRICS[category].values():
            str_lst.extend(gen_metric_str_lst(metric, True))

    print(_format(str_lst[1:], concise))
