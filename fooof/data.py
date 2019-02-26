"""   """

from collections import namedtuple

###################################################################################################
###################################################################################################

FOOOFResults = namedtuple('FOOOFResults', ['aperiodic_params', 'peak_params',
                                         'r_squared', 'error', 'gaussian_params'])

FOOOFSettings = namedtuple('FOOOFSettings', ['peak_width_limits', 'max_n_peaks',
                                             'min_peak_amplitude', 'peak_threshold',
                                             'aperiodic_mode'])

FOOOFResults.__doc__ = """\
The resulting parameters and associated data of a FOOOF model fit.

Attributes
----------
aperiodic_params : 1d array, len 2 or 3
    Parameters that define the aperiodic fit. As [Offset, (Knee), Exponent].
        The knee parameter is only included if aperiodic is fit with knee. Otherwise, length is 2.
peak_params : 2d array, shape=[n_peaks, 3]
    Fitted parameter values for the peaks. Each row is a peak, as [CF, Amp, BW].
r_squared : float
    R-squared of the fit between the input power spectrum and the full model fit.
error : float
    Root mean squared error of the full model fit.
gaussian_params : 2d array, shape=[n_peaks, 3]
    Parameters that define the gaussian fit(s). Each row is a gaussian, as [mean, amp, std].
"""

FOOOFSettings.__doc__ = """\
The user defined settings for a FOOOF object.

Attributes
----------
peak_width_limits : tuple of (float, float), optional, default: [0.5, 12.0]
    Limits on possible peak width, as [lower_bound, upper_bound].
max_n_peaks : int, optional, default: inf
    Maximum number of gaussians to be fit in a single spectrum.
min_peak_amplitude : float, optional, default: 0
    Minimum amplitude threshold for a peak to be modeled.
peak_threshold : float, optional, default: 2.0
    Threshold for detecting peaks, units of standard deviation.
aperiodic_mode : {'fixed', 'knee'}
    Which approach to take to fitting the aperiodic component.
"""