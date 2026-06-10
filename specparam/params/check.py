"""Functionality to check available parameter conversions."""

from specparam.reports.strings import _format
from specparam.modes.mode import VALID_COMPONENTS

###################################################################################################
###################################################################################################

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
