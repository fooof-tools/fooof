"""Define common base objects."""

from copy import deepcopy

import numpy as np

from specparam.data import ModelRunModes
from specparam.core.utils import unlog
from specparam.core.items import OBJ_DESC
from specparam.objs.fit import BaseFit, BaseFit2D, BaseFit2DT
from specparam.objs.data import BaseData, BaseData2D, BaseData2DT

###################################################################################################
###################################################################################################

class CommonBase():
    """Define CommonBase object."""

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

        if not self.has_data:
            raise NoDataError("No data available to fit, can not proceed.")
        assert space in ['linear', 'log'], "Input for 'space' invalid."

        if component == 'full':
            output = self.power_spectrum if space == 'log' else unlog(self.power_spectrum)
        elif component == 'aperiodic':
            output = self._spectrum_peak_rm if space == 'log' else \
                unlog(self.power_spectrum) / unlog(self._peak_fit)
        elif component == 'peak':
            output = self._spectrum_flat if space == 'log' else \
                unlog(self.power_spectrum) - unlog(self._ap_fit)
        else:
            raise ValueError('Input for component invalid.')

        return output


    def get_run_modes(self):
        """Return run modes of the current object.

        Returns
        -------
        ModelRunModes
            Object containing the run modes from the current object.
        """

        return ModelRunModes(**{key.strip('_') : getattr(self, key) \
                             for key in OBJ_DESC['run_modes']})


    def set_run_modes(self, debug, check_freqs, check_data):
        """Simultaneously set all run modes.

        Parameters
        ----------
        debug : bool
            Whether to run in debug mode.
        check_freqs : bool
            Whether to run in check freqs mode.
        check_data : bool
            Whether to run in check data mode.
        """

        self.set_debug_mode(debug)
        self.set_check_modes(check_freqs, check_data)


    def _add_from_dict(self, data):
        """Add data to object from a dictionary.

        Parameters
        ----------
        data : dict
            Dictionary of data to add to self.
        """

        for key in data.keys():
            setattr(self, key, data[key])


class BaseObject(CommonBase, BaseFit, BaseData):
    """Define Base object for fitting models to 1D data."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        CommonBase.__init__(self)
        BaseData.__init__(self)
        BaseFit.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
                         debug_mode=debug_mode, verbose=verbose)


    def add_data(self, freqs, power_spectrum, freq_range=None, clear_results=True):
        """Add data (frequencies, and power spectrum values) to the current object.

        Parameters
        ----------
        % copied in from Data object
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        % copied in from Data object
        """

        # Clear results, if present, unless indicated not to
        self._reset_results(clear_results=self.has_model and clear_results)

        super().add_data(freqs, power_spectrum, freq_range=None)


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False, clear_results=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        """

        self._reset_data(clear_freqs, clear_spectrum)
        self._reset_results(clear_results)


class BaseObject2D(CommonBase, BaseFit2D, BaseData2D):
    """Define Base object for fitting models to 2D data."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        CommonBase.__init__(self)
        BaseData2D.__init__(self)
        BaseFit2D.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
                           debug_mode=debug_mode, verbose=verbose)


    def add_data(self, freqs, power_spectra, freq_range=None, clear_results=True):
        """Add data (frequencies and power spectrum values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        power_spectra : 2d array, shape=[n_power_spectra, n_freqs]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if clear_results and np.any(self.freqs):
            self._reset_data_results(True, True, True, True)
            self._reset_group_results()

        super().add_data(freqs, power_spectra, freq_range=None)


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False,
                            clear_results=False, clear_spectra=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        clear_results : bool, optional, default: False
            Whether to clear model results attributes.
        clear_spectra : bool, optional, default: False
            Whether to clear power spectra attribute.
        """

        self._reset_data(clear_freqs, clear_spectrum, clear_spectra)
        self._reset_results(clear_results)


class BaseObject2DT(BaseObject2D, BaseFit2DT, BaseData2DT):
    """Define Base object for fitting models to 2D data - tranpose version."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        BaseObject2D.__init__(self)
        BaseData2DT.__init__(self)
        BaseFit2D.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
                           debug_mode=debug_mode, verbose=verbose)
