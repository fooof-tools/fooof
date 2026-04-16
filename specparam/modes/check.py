"""Functionality to check available modes."""

###################################################################################################
###################################################################################################

def check_modes(component='all', check_params=False):
    """Check the set of modes that are available.

    Parameters
    ----------
    component : {'all', 'aperiodic', 'periodic'}
        Which component to check available modes for.
    check_params : bool, optional, default: False
        Whether to print out information on the parameters of each mode.
    """

    from specparam.modes.definitions import MODES

    component = ['aperiodic', 'periodic'] if component == 'all' else [component]

    for comp in component:
        print('Available {:s} modes:'.format(comp))
        for mode in MODES[comp].values():
            if not check_params:
                print('    {:14s}    {:s}'.format(mode.name, mode.description))
            else:
                print('\n{:s}'.format(mode.name))
                print('    {:s}'.format(mode.description))
                mode.check_params()
