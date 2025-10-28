"""Modes object."""

from specparam.data import ModelModes
from specparam.modes.mode import Mode, VALID_COMPONENTS
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

        # Set list of component names
        self.components = VALID_COMPONENTS

        # Add mode definitions for each component
        self.aperiodic = check_mode_definition(aperiodic, AP_MODES)
        self.periodic = check_mode_definition(periodic, PE_MODES)


    def check_params(self):
        """Check the description of the parameters for each mode."""

        if self.aperiodic:
            self.aperiodic.check_params()
        if self.periodic:
            self.periodic.check_params()


    def get_modes(self):
        """Get the modes definition.

        Returns
        -------
        modes_def : ModelModes
            Modes definition.
        """

        return ModelModes(aperiodic_mode=self.aperiodic.name if self.aperiodic else None,
                          periodic_mode=self.periodic.name if self.periodic else None)


def check_mode_definition(mode, options):
    """Check a mode specification.

    Parameters
    ----------
    mode : str or None or Mode
        Fit mode. If str, should be a label corresponding to an entry in `options`.
    options : dict
        Available modes.

    Returns
    -------
    mode : Mode or None
        Mode object, if defined, or None if not defined.

    Raises
    ------
    ValueError
        If the mode definition is not found / understood.
    """

    if isinstance(mode, str):
        assert mode in list(options.keys()), 'Specific Mode not found.'
        mode = options[mode]

    if mode is None:
        mode = None
    elif not isinstance(mode, Mode):
        raise ValueError('Mode input not understood.')

    return mode
