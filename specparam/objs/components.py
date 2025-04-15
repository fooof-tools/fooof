"""Define model components object."""

from specparam.utils.array import unlog
from specparam.modutils.errors import NoModelError

###################################################################################################
###################################################################################################

class ModelComponents():
    """Object for managing model components.

    Attributes
    ----------
    modeled_spectrum : 1d array
        Modeled spectrum.
    _spectrum_flat : 1d array
        Data attribute: flattened power spectrum, with the aperiodic component removed.
    _spectrum_peak_rm : 1d array
        Data attribute: power spectrum, with peaks removed.
    _ap_fit : 1d array
        Model attribute: values of the isolated aperiodic fit.
    _peak_fit : 1d array
        Model attribute: values of the isolated peak fit.
    """

    def __init__(self):
        """Initialize ModelComponents object."""

        self.reset()


    def reset(self):
        """Reset model components attributes."""

        # Full model
        self.modeled_spectrum = None

        # Model components
        self._ap_fit = None
        self._peak_fit = None

        # Data components
        self._spectrum_flat = None
        self._spectrum_peak_rm = None


    def get_component(self, component='full', space='log'):
        """Get a model component.

        Parameters
        ----------
        component : {'full', 'aperiodic', 'peak'}
            Which model component to return.
                'full' - full model
                'aperiodic' - isolated aperiodic model component
                'peak' - isolated peak model component
        space : {'log', 'linear'}
            Which space to return the model component in.
                'log' - returns in log10 space.
                'linear' - returns in linear space.

        Returns
        -------
        output : 1d array
            Specified model component, in specified spacing.

        Notes
        -----
        The 'space' parameter doesn't just define the spacing of the model component
        values, but rather defines the space of the additive model such that
        `model = aperiodic_component + peak_component`.
        With space set as 'log', this combination holds in log space.
        With space set as 'linear', this combination holds in linear space.
        """

        if self.modeled_spectrum is None:
            raise NoModelError("No model fit results are available, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.modeled_spectrum if space == 'log' else unlog(self.modeled_spectrum)
        elif component == 'aperiodic':
            output = self._ap_fit if space == 'log' else unlog(self._ap_fit)
        elif component == 'peak':
            output = self._peak_fit if space == 'log' else \
                unlog(self.modeled_spectrum) - unlog(self._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output
