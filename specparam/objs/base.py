"""Define common base objects."""

from copy import deepcopy

import numpy as np

from specparam.data import ModelRunModes
from specparam.utils.array import unlog
from specparam.core.items import OBJ_DESC
from specparam.io.utils import get_files
from specparam.io.files import load_json, load_jsonlines
from specparam.io.models import save_model, save_group, save_event
from specparam.modutils.errors import NoDataError
from specparam.modutils.docs import copy_doc_func_to_method
from specparam.objs.results import BaseResults, BaseResults2D, BaseResults2DT, BaseResults3D
from specparam.objs.data import BaseData, BaseData2D, BaseData2DT, BaseData3D

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


class BaseObject(CommonBase, BaseResults, BaseData):
    """Define Base object for fitting models to 1D data."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        CommonBase.__init__(self)
        BaseData.__init__(self)
        BaseResults.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
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

        super().add_data(freqs, power_spectrum, freq_range=freq_range)


    @copy_doc_func_to_method(save_model)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_model(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None, regenerate=True):
        """Load in a data file to the current object.

        Parameters
        ----------
        file_name : str or FileObject
            File to load data from.
        file_path : Path or str, optional
            Path to directory to load from. If None, loads from current directory.
        regenerate : bool, optional, default: True
            Whether to regenerate the model fit from the loaded data, if data is available.
        """

        # Reset data in object, so old data can't interfere
        self._reset_data_results(True, True, True)

        # Load JSON file, add to self and check loaded data
        data = load_json(file_name, file_path)
        self._add_from_dict(data)
        self._check_loaded_settings(data)
        self._check_loaded_results(data)

        # Regenerate model components, based on what is available
        if regenerate:
            if self.freq_res:
                self._regenerate_freqs()
            if np.all(self.freqs) and np.all(self.aperiodic_params_):
                self._regenerate_model()


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


class BaseObject2D(CommonBase, BaseResults2D, BaseData2D):
    """Define Base object for fitting models to 2D data."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        CommonBase.__init__(self)
        BaseData2D.__init__(self)
        BaseResults2D.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
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

        super().add_data(freqs, power_spectra, freq_range=freq_range)


    @copy_doc_func_to_method(save_group)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_group(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None):
        """Load group data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : Path or str, optional
            Path to directory to load from. If None, loads from current directory.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_group_results()

        power_spectra = []
        for ind, data in enumerate(load_jsonlines(file_name, file_path)):

            self._add_from_dict(data)

            # If settings are loaded, check and update based on the first line
            if ind == 0:
                self._check_loaded_settings(data)

            # If power spectra data is part of loaded data, collect to add to object
            if 'power_spectrum' in data.keys():
                power_spectra.append(data['power_spectrum'])

            # If results part of current data added, check and update object results
            if set(OBJ_DESC['results']).issubset(set(data.keys())):
                self._check_loaded_results(data)
                self.group_results.append(self._get_results())

        # Reconstruct frequency vector, if information is available to do so
        if self.freq_range:
            self._regenerate_freqs()

        # Add power spectra data, if they were loaded
        if power_spectra:
            self.power_spectra = np.array(power_spectra)

        # Reset peripheral data from last loaded result, keeping freqs info
        self._reset_data_results(clear_spectrum=True, clear_results=True)


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


class BaseObject2DT(BaseObject2D, BaseResults2DT, BaseData2DT):
    """Define Base object for fitting models to 2D data - tranpose version."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        BaseObject2D.__init__(self)
        BaseData2DT.__init__(self)
        BaseResults2D.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
                               debug_mode=debug_mode, verbose=verbose)


    def load(self, file_name, file_path=None, peak_org=None):
        """Load time data from file.

        Parameters
        ----------
        file_name : str
            File to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        peak_org : int or Bands
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        # Clear results so as not to have possible prior results interfere
        self._reset_time_results()
        super().load(file_name, file_path=file_path)
        if peak_org is not False and self.group_results:
            self.convert_results(peak_org)


class BaseObject3D(BaseObject2DT, BaseResults3D, BaseData3D):
    """Define Base object for fitting models to 3D data."""

    def __init__(self, aperiodic_mode=None, periodic_mode=None, debug_mode=False, verbose=True):

        BaseObject2DT.__init__(self)
        BaseData3D.__init__(self)
        BaseResults3D.__init__(self, aperiodic_mode=aperiodic_mode, periodic_mode=periodic_mode,
                               debug_mode=debug_mode, verbose=verbose)


    def add_data(self, freqs, spectrograms, freq_range=None, clear_results=True):
        """Add data (frequencies and spectrograms) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        spectrograms : 3d array or list of 2d array
            Matrix of power values, in linear space.
            If a list of 2d arrays, each should be have the same shape of [n_freqs, n_time_windows].
            If a 3d array, should have shape [n_events, n_freqs, n_time_windows].
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.
        clear_results : bool, optional, default: True
            Whether to clear prior results, if any are present in the object.
            This should only be set to False if data for the current results are being re-added.

        Notes
        -----
        If called on an object with existing data and/or results these will be cleared
        by this method call, unless explicitly set not to.
        """

        if clear_results:
            self._reset_event_results()

        super().add_data(freqs, spectrograms, freq_range=freq_range)


    @copy_doc_func_to_method(save_event)
    def save(self, file_name, file_path=None, append=False,
             save_results=False, save_settings=False, save_data=False):

        save_event(self, file_name, file_path, append, save_results, save_settings, save_data)


    def load(self, file_name, file_path=None, peak_org=None):
        """Load data from file(s).

        Parameters
        ----------
        file_name : str
            File(s) to load data from.
        file_path : str, optional
            Path to directory to load from. If None, loads from current directory.
        peak_org : int or Bands, optional
            How to organize peaks.
            If int, extracts the first n peaks.
            If Bands, extracts peaks based on band definitions.
        """

        files = get_files(file_path, select=file_name)
        spectrograms = []
        for file in files:
            super().load(file, file_path, peak_org=False)
            if self.group_results:
                self.add_results(self.group_results, append=True)
            if np.all(self.power_spectra):
                spectrograms.append(self.spectrogram)
        self.spectrograms = np.array(spectrograms) if spectrograms else None

        self._reset_group_results()
        if peak_org is not False and self.event_group_results:
            self.convert_results(peak_org)


    def _reset_data_results(self, clear_freqs=False, clear_spectrum=False, clear_results=False,
                            clear_spectra=False, clear_spectrograms=False):
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
        clear_spectrograms : bool, optional, default: False
            Whether to clear spectrograms attribute.
        """

        self._reset_data(clear_freqs, clear_spectrum, clear_spectra, clear_spectrograms)
        self._reset_results(clear_results)
