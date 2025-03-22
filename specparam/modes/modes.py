"""Modes object."""

from specparam.modes.mode import Mode
from specparam.modes.definitions import AP_MODES, PE_MODES

###################################################################################################
###################################################################################################

class Modes():
    """Defines a set of fit modes.

    Parameters
    ----------
    aperiodic : str or Mode
        Aperiodic mode.
    periodic : str or Mode
        Periodic mode.
    """

    def __init__(self, aperiodic, periodic):
        """Initialize modes."""

        self.aperiodic = check_mode_definition(aperiodic, AP_MODES)
        self.periodic = check_mode_definition(periodic, PE_MODES)



def check_mode_definition(mode, options):
    """Check a mode specification.

    Parameters
    ----------
    mode : str or Mode
        Fit mode. If str, should be a label corresponding to an entry in `options`.
    options : dict
        Available modes.

    Raises
    ------
    ValueError
        If the mode definition is not found / understood.
    """

    if isinstance(mode, str):
        assert mode in list(options.keys()), 'Specific Mode not found.'
        mode = options[mode]
    elif isinstance(mode, Mode):
        mode = mode
    else:
        raise ValueError('Mode input not understood.')

    return mode
