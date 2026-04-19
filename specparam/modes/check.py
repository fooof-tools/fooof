"""Functionality to check available modes."""

from specparam.modes.mode import VALID_COMPONENTS
from specparam.reports.strings import gen_mode_str_lst, _format

###################################################################################################
###################################################################################################

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

        str_lst.extend(['', 'AVAILABLE {} MODES'.format(component.upper()), ''])

        for mode in MODES[component].values():
            str_lst.extend(gen_mode_str_lst(mode, True, label_component=False))

    print(_format(str_lst[1:], concise))

    # for comp in component:
    #     print('Available {:s} modes:'.format(comp))
    #     for mode in MODES[comp].values():
    #         if not check_params:
    #             print('    {:15s}    {:s}'.format(mode.name, mode.description))
    #         else:
    #             print('\n{:s}'.format(mode.name))
    #             print('    {:s}'.format(mode.description))
    #             mode.check_params()
