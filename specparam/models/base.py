"""Define common base objects."""

from copy import deepcopy

from specparam.utils.checks import check_array_dim
from specparam.modes.modes import Modes
from specparam.modutils.errors import NoDataError
from specparam.reports.strings import gen_issue_str

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

    def __init__(self, aperiodic_mode, periodic_mode, converters, verbose):
        """Initialize object."""

        self.add_modes(aperiodic_mode, periodic_mode)
        self._converters = converters
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

        self.modes = Modes(aperiodic=aperiodic_mode, periodic=periodic_mode, model=self)

        if getattr(self, 'results', None):
            self.results.modes = self.modes
            self.results._reset_results()

        if getattr(self, 'algorithm', None):
            self.algorithm._reset_subobjects(modes=self.modes, results=self.results)


    def print(self, info, description=False, concise=False):
        """Print out information.

        Parameters
        ----------
        info : {'algorithm', 'settings', 'data', 'modes', 'issue'}
            Which information to print:
                'algorithm' or 'settings': print information on the fit algorithm & settings
                'data' : print a description of the data
                'modes' : print a description of the fit modes
                'issue' : print instructions on how to report bugs and/or problematic fits
        description : bool, optional, default: False
            Whether to print out a description with current settings.
        concise : bool, optional, default: False
            Whether to print the report in a concise mode.
        """

        # Special case - treat 'settings' as request to print algorithm info
        if info == 'settings':
            info = 'algorithm'

        if info in ['algorithm', 'data', 'modes']:
            getattr(self, info).print(concise=concise)

        elif info == 'issue':
            print(gen_issue_str(concise))

        else:
            raise ValueError('Requested info input for printing not understood.')


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to current object.
        """

        # Catch and add custom objects
        if 'aperiodic_mode' in data.keys() and 'periodic_mode' in data.keys():
            self.add_modes(aperiodic_mode=data.pop('aperiodic_mode'),
                           periodic_mode=data.pop('periodic_mode'))
        if 'bands' in data.keys():
            self.results.add_bands(data.pop('bands'))
        if 'metrics' in data.keys():
            tmetrics = data.pop('metrics')
            self.results.add_metrics(list(tmetrics.keys()))
            self.results.metrics.add_results(tmetrics)
        # TODO
        for label, params in {ke : va for ke, va in data.items() if '_fit' in ke or '_converted' in ke}.items():
            if 'peak' in label:
                params = check_array_dim(params)
            label1, label2 = label.split('_')
            component = 'periodic' if label1 == 'peak' else label1
            getattr(self.results.params, component).add_params(label2, params)
            #setattr(self.results.params, label.split('_')[0], params)

        # Add additional attributes directly to object
        for key in data.keys():
            if getattr(self.algorithm.settings, key, False) is not False:
                setattr(self.algorithm.settings, key, data[key])
            elif getattr(self.data, key, False) is not False:
                setattr(self.data, key, data[key])
