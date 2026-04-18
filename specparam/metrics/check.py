"""Functionality to check available metrics."""

from specparam.reports.settings import LCV
from specparam.reports.strings import gen_metrics_str

###################################################################################################
###################################################################################################

def check_metrics(category='all'):
    """Check the set of available metrics.

    Parameters
    ----------
    category : {'all', 'error', 'gof'}
        Which category of metrics to check.
    """

    from specparam.metrics.metrics import Metrics
    from specparam.metrics.definitions import METRICS

    category = ['error', 'gof'] if category == 'all' else [category]

    out = ''
    for cat in category:

        met_str = gen_metrics_str(Metrics(METRICS[cat].values()), True)
        met_str = met_str.replace('CURRENT METRICS', 'AVAILABLE {} METRICS'.format(cat.upper()))
        out += met_str

    out = out.replace('\n' + '=' * LCV * 2 + '\n', '')

    print(out)
