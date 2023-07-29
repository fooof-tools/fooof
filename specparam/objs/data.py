"""   """

import numpy as np

from specparam.sim.gen import gen_freqs
from specparam.utils.data import trim_spectrum
from specparam.core.items import OBJ_DESC
from specparam.core.errors import DataError, InconsistentDataError
from specparam.data import SpectrumMetaData
from specparam.plts.settings import PLT_COLORS
from specparam.plts.spectra import plot_spectra
from specparam.plts.utils import check_plot_kwargs

###################################################################################################
###################################################################################################

class BaseData():
    """Base object for managing data for spectral parameterization.

    Parameters
    ----------
    _check_freqs : bool
        Run mode: whether to check the frequency values.
        If True, checks the frequency values, and raises an error for uneven spacing.
    _check_data : bool
        Run mode: whether to check the power spectrum values.
        If True, checks the power values and raises an error for any NaN / Inf values.
    """

    def __init__(self, check_freqs_mode=True, check_data_mode=True):

        self._reset_data(True, True)

        # Define data check run modes
        self._check_freqs = check_freqs_mode
        self._check_data = check_data_mode


    @property
    def has_data(self):
        """Indicator for if the object contains data."""

        return True if np.any(self.power_spectrum) else False


    def add_data(self, freqs, power_spectrum, freq_range=None):
        """Add data (frequencies, and power spectrum values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectrum, in linear space.
        power_spectrum : 1d array
            Power spectrum values, which must be input in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectrum to.
            If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data it will be cleared by this method call.
        """

        # If any data is already present, then clear previous data
        #   This is to ensure object consistency of all data & results
        self._reset_data(clear_freqs=self.has_data, clear_spectrum=self.has_data)

        self.freqs, self.power_spectrum, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, power_spectrum, freq_range, 1)


    def add_meta_data(self, meta_data):
        """Add data information into object from a SpectrumMetaData object.

        Parameters
        ----------
        meta_data : SpectrumMetaData
            A meta data object containing meta data information.
        """

        for meta_dat in OBJ_DESC['meta_data']:
            setattr(self, meta_dat, getattr(meta_data, meta_dat))

        self._regenerate_freqs()


    def get_meta_data(self):
        """Return data information from the current object.

        Returns
        -------
        SpectrumMetaData
            Object containing meta data from the current object.
        """

        return SpectrumMetaData(**{key : getattr(self, key) \
            for key in OBJ_DESC['meta_data']})


    def plot(self, plt_log=False, **plt_kwargs):
        """Plot the power spectrum."""

        data_kwargs = check_plot_kwargs(\
            plt_kwargs, {'color' : PLT_COLORS['data'], 'linewidth' : 2.0})
        plot_spectra(self.freqs, self.power_spectrum, log_freqs=plt_log,
                     log_powers=False, **data_kwargs)


    def set_check_modes(self, check_freqs=None, check_data=None):
        """Set check modes, which controls if an error is raised based on check on the inputs.

        Parameters
        ----------
        check_freqs : bool, optional
            Whether to run in check freqs mode, which checks the frequency data.
        check_data : bool, optional
            Whether to run in check data mode, which checks the power spectrum values data.
        """

        if check_freqs is not None:
            self._check_freqs = check_freqs
        if check_data is not None:
            self._check_data = check_data


    def _reset_data(self, clear_freqs=False, clear_spectrum=False):
        """Set, or reset, data & results attributes to empty.

        Parameters
        ----------
        clear_freqs : bool, optional, default: False
            Whether to clear frequency attributes.
        clear_spectrum : bool, optional, default: False
            Whether to clear power spectrum attribute.
        """

        if clear_freqs:
            self.freqs = None
            self.freq_range = None
            self.freq_res = None

        if clear_spectrum:
            self.power_spectrum = None


    def _regenerate_freqs(self):
        """Regenerate the frequency vector, given the object metadata."""

        self.freqs = gen_freqs(self.freq_range, self.freq_res)


    def _prepare_data(self, freqs, power_spectrum, freq_range, spectra_dim=1):
        """Prepare input data for adding to current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear space.
        power_spectrum : 1d or 2d array
            Power values, which must be input in linear space.
            1d vector, or 2d as [n_power_spectra, n_freqs].
        freq_range : list of [float, float]
            Frequency range to restrict power spectrum to.
            If None, keeps the entire range.
        spectra_dim : int, optional, default: 1
            Dimensionality that the power spectra should have.

        Returns
        -------
        freqs : 1d array
            Frequency values for the power_spectrum, in linear space.
        power_spectrum : 1d or 2d array
            Power spectrum values, in log10 scale.
            1d vector, or 2d as [n_power_specta, n_freqs].
        freq_range : list of [float, float]
            Minimum and maximum values of the frequency vector.
        freq_res : float
            Frequency resolution of the power spectrum.

        Raises
        ------
        DataError
            If there is an issue with the data.
        InconsistentDataError
            If the input data are inconsistent size.
        """

        # Check that data are the right types
        if not isinstance(freqs, np.ndarray) or not isinstance(power_spectrum, np.ndarray):
            raise DataError("Input data must be numpy arrays.")

        # Check that data have the right dimensionality
        if freqs.ndim != 1 or (power_spectrum.ndim != spectra_dim):
            raise DataError("Inputs are not the right dimensions.")

        # Check that data sizes are compatible
        if freqs.shape[-1] != power_spectrum.shape[-1]:
            raise InconsistentDataError("The input frequencies and power spectra "
                                        "are not consistent size.")

        # Check if power values are complex
        if np.iscomplexobj(power_spectrum):
            raise DataError("Input power spectra are complex values. "
                            "Model fitting does not currently support complex inputs.")

        # Force data to be dtype of float64
        #   If they end up as float32, or less, scipy curve_fit fails (sometimes implicitly)
        if freqs.dtype != 'float64':
            freqs = freqs.astype('float64')
        if power_spectrum.dtype != 'float64':
            power_spectrum = power_spectrum.astype('float64')

        # Check frequency range, trim the power_spectrum range if requested
        if freq_range:
            freqs, power_spectrum = trim_spectrum(freqs, power_spectrum, freq_range)

        # Check if freqs start at 0 and move up one value if so
        #   Aperiodic fit gets an inf if freq of 0 is included, which leads to an error
        if freqs[0] == 0.0:
            freqs, power_spectrum = trim_spectrum(freqs, power_spectrum, [freqs[1], freqs.max()])
            if self.verbose:
                print("\nFITTING WARNING: Skipping frequency == 0, "
                      "as this causes a problem with fitting.")

        # Calculate frequency resolution, and actual frequency range of the data
        freq_range = [freqs.min(), freqs.max()]
        freq_res = freqs[1] - freqs[0]

        # Log power values
        power_spectrum = np.log10(power_spectrum)

        ## Data checks - run checks on inputs based on check modes

        if self._check_freqs:
            # Check if the frequency data is unevenly spaced, and raise an error if so
            freq_diffs = np.diff(freqs)
            if not np.all(np.isclose(freq_diffs, freq_res)):
                raise DataError("The input frequency values are not evenly spaced. "
                                "The model expects equidistant frequency values in linear space.")
        if self._check_data:
            # Check if there are any infs / nans, and raise an error if so
            if np.any(np.isinf(power_spectrum)) or np.any(np.isnan(power_spectrum)):
                error_msg = ("The input power spectra data, after logging, contains NaNs or Infs. "
                             "This will cause the fitting to fail. "
                             "One reason this can happen is if inputs are already logged. "
                             "Input data should be in linear spacing, not log.")
                raise DataError(error_msg)

        return freqs, power_spectrum, freq_range, freq_res


class BaseData2D(BaseData):
    """   """

    def __init__(self):

        BaseData.__init__(self)

        self.power_spectra = None


    @property
    def has_data(self):
        """Indicator for if the object contains data."""

        return True if np.any(self.power_spectra) else False


    def add_data(self, freqs, power_spectra, freq_range=None):
        """Add data (frequencies and power spectrum values) to the current object.

        Parameters
        ----------
        freqs : 1d array
            Frequency values for the power spectra, in linear space.
        power_spectra : 2d array, shape=[n_power_spectra, n_freqs]
            Matrix of power values, in linear space.
        freq_range : list of [float, float], optional
            Frequency range to restrict power spectra to. If not provided, keeps the entire range.

        Notes
        -----
        If called on an object with existing data and/or results
        these will be cleared by this method call.
        """

        # If any data is already present, then clear data & results
        #   This is to ensure object consistency of all data & results
        if np.any(self.freqs):
            self._reset_data_results(True, True, True, True)
            self._reset_group_results()

        self.freqs, self.power_spectra, self.freq_range, self.freq_res = \
            self._prepare_data(freqs, power_spectra, freq_range, 2)
