"""Data objects for ERPparam.

Notes on ERPparam data objects:
- these data objects are NamedTuples, immutable data types with attribute labels
- the namedtuples are wrapped as classes (they are still immutable when doing this)
- wrapping in objects helps to be able to render well formed documentation for them.
- setting `__slots__` as empty voids the dynamic dictionary that usually stores attributes
    - this means no additional attributes can be defined (which is more memory efficient)
"""

from collections import namedtuple

###################################################################################################
###################################################################################################

class ERPparamSettings(namedtuple('ERPparamSettings', ['peak_width_limits', 'max_n_peaks',
                                                 'min_peak_height', 'peak_threshold', 'rectify'])):
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
    rectify : bool
        Whether to rectify the signal prior to fitting.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class ERPparamMetaData(namedtuple('ERPparamMetaData', ['time_range', 'fs'])):
    """Metadata information about a power spectrum.

    Parameters
    ----------
    time_range : list of [float, float]
        Time range of the signal, as [start_time, end_time].
    fs : float
        Sampling frequency of the signal.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class ERPparamResults(namedtuple('ERPparamResults', ['peak_params', 'r_squared', 'error', 
                                                     'gaussian_params','shape_params'])):
    """Model results from parameterizing a power spectrum.

    Parameters
    ----------
    peak_params : 2d array
        Fitted parameter values for the peaks. Each row is a peak, as [CF, PW, BW].
    r_squared : float
        R-squared of the fit between the full model fit and the input data.
    error : float
        Error of the full model fit.
    gaussian_params : 2d array
        Parameters that define the gaussian fit( s).
        Each row is a gaussian, as [mean, height, standard deviation].
    shape_params : 2d array
        ERP sghape parameters 
        Each row is a waveform, as [FWHM, rise-time, decay-time, rise-decay symmetry,
        sharpness, rising sharpeness, decaying sharpeness].

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()


class SimParams(namedtuple('SimParams', ['periodic_params', 'nlv'])):
    """Parameters that define a simulated power spectrum.

    Parameters
    ----------
    periodic_params : list or list of lists
        Parameters that define the periodic component.
    nlv : float
        Noise level added to simulated spectrum.

    Notes
    -----
    This object is a data object, based on a NamedTuple, with immutable data attributes.
    """
    __slots__ = ()
