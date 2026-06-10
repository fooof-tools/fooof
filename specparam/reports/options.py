"""Utilities to report on available options for fitting, modes, evaluations, etc."""

from specparam.modes.mode import VALID_COMPONENTS
from specparam.reports.strings import gen_mode_str_lst, gen_mode_params_str_lst, gen_metric_str_lst
from specparam.reports.strings import _format

###################################################################################################
###################################################################################################

def check_algorithms(concise=False):
    """Check the set of available fit algorithms."""

    from specparam.algorithms.definitions import ALGORITHMS

    str_lst = []
    str_lst.extend(['AVAILABLE ALGORITHMS', ''])

    for algorithm in ALGORITHMS.values():
        str_lst.append('{:s} : {:s}'.format(algorithm.name, algorithm.description))

    print(_format(str_lst, concise))


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

        str_lst.extend(['AVAILABLE {} METRICS'.format(category.upper()), ''])

        for metric in METRICS[category].values():
            str_lst.extend(gen_metric_str_lst(metric, True))

    print(_format(str_lst, concise))


def check_modes(component='all', check_params=False, concise=False):
    """Check the set of modes that are available.

    Parameters
    ----------
    component : {'all', 'aperiodic', 'periodic'}
        Which component to check available modes for.
    check_params : bool, optional, default: False
        Whether to print out information on the parameters of each mode.
    """

    from specparam.modes.definitions import MODES

    components = VALID_COMPONENTS if component == 'all' else [component]

    str_lst = []
    for component in components:

        str_lst.extend(['AVAILABLE {} MODES'.format(component.upper()), ''])

        for mode in MODES[component].values():
            str_lst.extend(gen_mode_str_lst(mode, True, label_component=False))
            if check_params:
                str_lst.extend(gen_mode_params_str_lst(mode))
                str_lst.append('')

    print(_format(str_lst, concise))


def check_converters(component='all', concise=False):
    """Check the set of parameter converters that are available.

    Parameters
    ----------
    component : {'all', 'aperiodic', 'periodic'}
        Which component to check available parameter converters for.
    """

    from specparam.params.definitions import CONVERTERS

    components = VALID_COMPONENTS if component == 'all' else [component]

    str_lst = []
    for component in components:

        str_lst.extend(['AVAILABLE {} PARAMETER CONVERTERS'.format(component.upper()), ''])

        for param, convs in CONVERTERS[component].items():
            str_lst.append("'" + param + "'")
            for label, converter in convs.items():
                str_lst.append('{:s}: {:s}'.format(converter.name, converter.description))

    print(_format(str_lst, concise))
