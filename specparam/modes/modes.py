"""Modes object."""

from specparam.data import ModelModes
from specparam.modes.mode import VALID_COMPONENTS
from specparam.modes.definitions import check_mode_definition, AP_MODES, PE_MODES
from specparam.reports.strings import gen_modes_str

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


    def print(self, description=False, concise=False):
        """Print out the current fit modes.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current fit modes.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_modes_str(self, description, concise))
