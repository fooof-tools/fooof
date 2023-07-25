"""Data objects.

Notes on data objects:
- these data objects are NamedTuples, immutable data types with attribute labels
- the namedtuples are wrapped as classes (they are still immutable when doing this)
- wrapping in objects helps to be able to render well formed documentation for them.
- setting `__slots__` as empty voids the dynamic dictionary that usually stores attributes
    - this means no additional attributes can be defined (which is more memory efficient)
"""

from collections import namedtuple

###################################################################################################
###################################################################################################

class ModelSettings(namedtuple('ModelSettings', ['peak_width_limits', 'max_n_peaks',
                                                 'min_peak_height', 'peak_threshold',
                                                 'aperiodic_mode'])):
    """User defined settings for the fitting algorithm.

    Parameters
    ----------
    peak_width_limits : tuple of (float, float)
        Limits on possible peak width, in Hz, as (lower_bound, upper_bound).
    max_n_peaks : int
        Maximum number of peaks to fit.
    min_peak_height : float
        Absolute threshold for detecting peaks, in units of the input data.
    peak_threshold : float
        Relative threshold for detecting peaks, in units of standard deviation of the input data.
    aperiodic_mode : {'fixed', 'knee'}
        Which approach to take for fitting the aperiodic component.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class ModelRunModes(namedtuple('ModelRunModes', ['debug', 'check_freqs', 'check_data'])):
    """Checks performed and errors raised by the model.

    Parameters
    ----------
    debug :  bool
       Whether to run in debug mode.
    check_freqs : bool
        Whether to run in check freqs mode.
    check_data : bool
        Whether to run in check data mode.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class SpectrumMetaData(namedtuple('SpectrumMetaData', ['freq_range', 'freq_res'])):
    """Metadata information about a power spectrum.

    Parameters
    ----------
    freq_range : list of [float, float]
        Frequency range of the power spectrum, as [lowest_freq, highest_freq].
    freq_res : float
        Frequency resolution of the power spectrum.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class FitResults(namedtuple('FitResults', ['aperiodic_params', 'peak_params',
                                           'r_squared', 'error', 'gaussian_params'])):
    """Model results from parameterizing a power spectrum.

    Parameters
    ----------
    aperiodic_params : 1d array
        Parameters that define the aperiodic fit. As [Offset, (Knee), Exponent].
        The knee parameter is only included if aperiodic is fit with knee.
    peak_params : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CF, PW, BW].
    r_squared : float
        R-squared of the fit between the full model fit and the input data.
    error : float
        Error of the full model fit.
    gaussian_params : 2d array
        Parameters that define the gaussian fit(s).
        Each row is a gaussian, as [mean, height, standard deviation].

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class SimParams(namedtuple('SimParams', ['aperiodic_params', 'periodic_params', 'nlv'])):
    """Parameters that define a simulated power spectrum.

    Parameters
    ----------
    aperiodic_params : list
        Parameters that define the aperiodic component.
    periodic_params : list or list of lists
        Parameters that define the periodic component.
    nlv : float
        Noise level added to simulated spectrum.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()
