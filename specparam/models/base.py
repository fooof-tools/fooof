"""Define common base objects."""

from copy import deepcopy

from specparam.utils.array import unlog
from specparam.utils.checks import check_array_dim
from specparam.modes.modes import Modes
from specparam.modutils.errors import NoDataError
from specparam.reports.strings import gen_modes_str, gen_settings_str, gen_issue_str

###################################################################################################
###################################################################################################

class BaseModel():
    """Define BaseModel object.

    Parameters
    ----------
    aperiodic_mode : Mode or str
        Mode for aperiodic component, or string specifying which mode to use.
    periodic_mode : Mode or str
        Mode for periodic component, or string specifying which mode to use.
    verbose : bool
        Whether to print out updates from the object.

    Attributes
    ----------
    modes : Modes
        Fit modes definitions.
    verbose : bool
        Verbosity status.
    """

    def __init__(self, aperiodic_mode, periodic_mode, verbose):
        """Initialize object."""

        self.add_modes(aperiodic_mode, periodic_mode)
        self.verbose = verbose


    def copy(self):
        """Return a copy of the current object."""

        return deepcopy(self)


    def add_modes(self, aperiodic_mode, periodic_mode):
        """Add modes definition to the object.

        Parameters
        ----------
        aperiodic_mode : Mode or str
            Mode for aperiodic component, or string specifying which mode to use.
        periodic_mode : Mode or str
            Mode for periodic component, or string specifying which mode to use.
        """

        self.modes = Modes(aperiodic=aperiodic_mode, periodic=periodic_mode)

        if getattr(self, 'results', None):
            self.results.modes = self.modes
            self.results._reset_results()

        if getattr(self, 'algorithm', None):
            self.algorithm._reset_subobjects(modes=self.modes, results=self.results)


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
            output = self.results.model._spectrum_peak_rm if space == 'log' else \
                unlog(self.data.power_spectrum) / unlog(self.results.model._peak_fit)
        elif component == 'peak':
            output = self.results.model._spectrum_flat if space == 'log' else \
                unlog(self.data.power_spectrum) - unlog(self.results.model._ap_fit)
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

        # Catch and add convert custom objects
        if 'aperiodic_mode' in data.keys() and 'periodic_mode' in data.keys():
            self.add_modes(aperiodic_mode=data.pop('aperiodic_mode'),
                           periodic_mode=data.pop('periodic_mode'))
        if 'bands' in  data.keys():
            self.results.add_bands(data.pop('bands'))
        if 'metrics' in data.keys():
            tmetrics = data.pop('metrics')
            self.results.add_metrics(list(tmetrics.keys()))
            self.results.metrics.add_results(tmetrics)
        for label, params in {key : vals for key, vals in data.items() if 'params' in key}.items():
            if 'peak' in label or 'gaussian' in label:
                params = check_array_dim(params)
            setattr(self.results.params, label.split('_')[0], params)

        # Add additional attributes directly to object
        for key in data.keys():
            if getattr(self.algorithm, key, False) is not False:
                setattr(self.algorithm, key, data[key])
            elif getattr(self.data, key, False) is not False:
                setattr(self.data, key, data[key])
