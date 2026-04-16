"""Functionality to check available modes."""

###################################################################################################
###################################################################################################

def check_modes(component, check_params=False):
    """Check the set of modes that are available.

    Parameters
    ----------
    component : {'aperiodic', 'periodic'}
        Which component to check available modes for.
    check_params : bool, optional, default: False
        Whether to print out information on the parameters of each mode.
    """

    from specparam.modes.definitions import MODES

    print('Available {:s} modes:'.format(component))
    for mode in MODES[component].values():
        if not check_params:
            print('    {:10s}    {:s}'.format(mode.name, mode.description))
        else:
            print('\n{:s}'.format(mode.name))
            print('    {:s}'.format(mode.description))
            mode.check_params()
