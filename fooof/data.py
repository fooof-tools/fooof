"""Data objects for FOOOF."""

from collections import namedtuple

###################################################################################################
###################################################################################################

FOOOFSettings = namedtuple('FOOOFSettings', ['peak_width_limits', 'max_n_peaks',
                                             'min_peak_height', 'peak_threshold',
                                             'aperiodic_mode'])
FOOOFSettings.__doc__ = """\
The user defined settings for a FOOOF object.

Attributes
----------
peak_width_limits : tuple of (float, float), optional, default: (0.5, 12.0)
    Limits on possible peak width, as (lower_bound, upper_bound).
max_n_peaks : int, optional, default: inf
    Maximum number of gaussians to be fit in a single spectrum.
min_peak_height : float, optional, default: 0
    Absolute threshold for detecting peaks, in units of the input data.
peak_threshold : float, optional, default: 2.0
    Relative threshold for detecting peaks, in units of standard deviation of the input data.
aperiodic_mode : {'fixed', 'knee'}
    Which approach to take for fitting the aperiodic component.
"""


FOOOFMetaData = namedtuple('FOOOFMetaData', ['freq_range', 'freq_res'])

FOOOFMetaData.__doc__ = """\
Data related information for a FOOOF object.

Attributes
----------
freq_range : list of [float, float]
    Frequency range of the power spectrum, as [lowest_freq, highest_freq].
freq_res : float
    Frequency resolution of the power spectrum.
"""


FOOOFResults = namedtuple('FOOOFResults', ['aperiodic_params', 'peak_params',
                                           'r_squared', 'error', 'gaussian_params'])
FOOOFResults.__doc__ = """\
The resulting parameters and associated data of a FOOOF model fit.

Attributes
----------
aperiodic_params : 1d array
    Parameters that define the aperiodic fit. As [Offset, (Knee), Exponent].
    The knee parameter is only included if aperiodic is fit with knee.
peak_params : 2d array
    Fitted parameter values for the peaks. Each row is a peak, as [CF, PW, BW].
r_squared : float
    R-squared of the fit between the input power spectrum and the full model fit.
error : float
    Root mean squared error of the full model fit.
gaussian_params : 2d array
    Parameters that define the gaussian fit(s).
    Each row is a gaussian, as [mean, height, standard deviation].
"""


SimParams = namedtuple('SimParams', ['aperiodic_params', 'gaussian_params', 'nlv'])

SimParams.__doc__ = """\
Stores parameters used to simulate a single power spectra.

Attributes
----------
aperiodic_params : list, len 2 or 3
    Parameters that define the aperiodic fit. As [Offset, (Knee), Exponent].
    The knee parameter is only included if aperiodic is fit with knee. Otherwise, length is 2.
gaussian_params : list or list of lists
    Fitted parameter values for the peaks.
    Each list is a peak, with a gaussian definition of [mean, height, standard deviation].
nlv : float
    Noise level added to the generated power spectrum.
"""
