"""Define common base objects."""

from copy import deepcopy

from specparam.utils.array import unlog
from specparam.modes.modes import Modes
from specparam.modutils.errors import NoDataError
from specparam.objs.metrics import Metrics
from specparam.reports.strings import gen_modes_str, gen_settings_str, gen_issue_str

###################################################################################################
###################################################################################################

class BaseModel():
    """Define BaseModel object."""

    def __init__(self, aperiodic_mode, periodic_mode, verbose):
        """Initialize object."""

        self.modes = Modes(aperiodic=aperiodic_mode, periodic=periodic_mode)

        self.metrics = Metrics()
        self.metrics.set_defaults()

        self.verbose = verbose


    def copy(self):
        """Return a copy of the current object."""

        return deepcopy(self)


    def get_data(self, component='full', space='log'):
        """Get a data component.

        Parameters
        ----------
        component : {'full', 'aperiodic', 'peak'}
            Which data component to return.
                'full' - full power spectrum
                'aperiodic' - isolated aperiodic data component
                'peak' - isolated peak data component
        space : {'log', 'linear'}
            Which space to return the data component in.
                'log' - returns in log10 space.
                'linear' - returns in linear space.

        Returns
        -------
        output : 1d array
            Specified data component, in specified spacing.

        Notes
        -----
        The 'space' parameter doesn't just define the spacing of the data component
        values, but rather defines the space of the additive data definition such that
        `power_spectrum = aperiodic_component + peak_component`.
        With space set as 'log', this combination holds in log space.
        With space set as 'linear', this combination holds in linear space.
        """

        if not self.data.has_data:
            raise NoDataError("No data available to fit, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.data.power_spectrum if space == 'log' \
                else unlog(self.data.power_spectrum)
        elif component == 'aperiodic':
            output = self.results._spectrum_peak_rm if space == 'log' else \
                unlog(self.data.power_spectrum) / unlog(self.results._peak_fit)
        elif component == 'peak':
            output = self.results._spectrum_flat if space == 'log' else \
                unlog(self.data.power_spectrum) - unlog(self.results._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output


    def print_modes(self, description=False, concise=False):
        """Print out the current fit modes.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current fit modes.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_modes_str(self, description, concise))


    def print_settings(self, description=False, concise=False):
        """Print out the current settings.

        Parameters
        ----------
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_settings_str(self, description, concise))


    @staticmethod
    def print_report_issue(concise=False):
        """Prints instructions on how to report bugs and/or problematic fits.

        Parameters
        ----------
        concise : bool, optional, default: False
            Whether to print the report in a concise mode, or not.
        """

        print(gen_issue_str(concise))


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        for key in data.keys():
            if getattr(self, key, False) is not False:
                setattr(self, key, data[key])
            elif getattr(self.data, key, False) is not False:
                setattr(self.data, key, data[key])
            elif getattr(self.results, key, False) is not False:
                setattr(self.results, key, data[key])


    def _check_loaded_modes(self, data):
        """Check if fit modes added, and update the object as needed.

        Parameters
        ----------
        data : dict
            A dictionary of data that has been added to the object.
        """

        # TEMP / ToDo: not quite clear if this is the right place
        #   And/or - might want a clearer process to 'reset' Modes

        if 'aperiodic_mode' in data and 'periodic_mode' in data:
            self.modes = Modes(aperiodic=data['aperiodic_mode'],
                               periodic=data['periodic_mode'])
