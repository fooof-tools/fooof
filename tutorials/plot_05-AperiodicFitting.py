"""
05: Aperiodic Component Fitting
===============================
"""

###################################################################################################
#
# This tutorials covers how to choose and use different approaches for
# fitting the aperiodic component of the signal.
#

###################################################################################################

# Import numpy for loading data, and FOOOF object
import numpy as np
from fooof import FOOOF

###################################################################################################
# Aperiodic Fitting Approaches
# ----------------------------
#
# FOOOF currently offers two approaches for fitting the aperiodic component:
#
# - Fitting with just an offset and a exponent, equivalent to a linear fit in log-log space
#
#   - `aperiodic_mode` = 'fixed'
# - Including a 'knee' parameter, reflecting a fit with a bend, in log-log space
#
#   - `aperiodic_mode` = 'knee'
#
# Fitting in the 'fixed' mode assumes a single 1/f like characteristic to the aperiodic
# signal, meaning it looks linear across all frequencies in log-log space.
#
# Though this assumption is true across *some* frequency ranges in neural data, it does
# does not hold up across broad freequency ranges. If fitting is done in the 'fixed' mode,
# but the assumption of a single 1/f is violated, then fitting will go wrong.
#
# Broad frequency ranges (typically ranges greater than ~40 Hz range) don't meet this
# criterion, as they typically exhibit a 'bend' in the aperiodic signal, whereby there is
# not a single 1/f property across all frequencies, but rather a 'bend' in the aperiodic
# component. For these cases, fitting should be done using an extra parameter to capture
# this, in 'knee' mode.
#

###################################################################################################
# Fitting FOOOF with Aperiodic 'Knee'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

###################################################################################################

# Load example data (LFP)
freqs = np.load('dat/freqs_lfp.npy')
spectrum = np.load('dat/spectrum_lfp.npy')

###################################################################################################

# Initialize FOOOF - setting to aperiodic mode to use a knee fit
fm = FOOOF(peak_width_limits=[2, 8], aperiodic_mode='knee')

###################################################################################################

# Fit FOOOF model
#  Note that this time we're specifying an optional parameter to plot in log-log
fm.report(freqs, spectrum, [2, 60], plt_log=True)

###################################################################################################
# A note on interpreting the "knee" parameter
# -------------------------------------------
#
# The aperiodic fit has the form:
#
# .. math::
#    AP = 10^b * \ \frac{1}{(k + F^\chi)}
#
# The knee parameter reported above corresponds to `k` in the equation.
#
# This parameter is dependent on the frequency at which the aperiodic fit
# transitions from horizontal to negatively sloped.
#
# To interpret this parameter as a frequency, take the :math:`\chi`-th root of `k`, i.e.:
#
# .. math::
#    knee \ frequency = k^{1/\ \chi}
#
# Interpreting the fit results when using knee fits is more complex, as the exponent result is
# no longer a simple measure of the aperiodic component as a whole, but instead reflects the
# aperiodic component past the 'knee' inflecting point. Becaues of this, when doing knee fits,
# knee & exponent values should be considered together.
#

###################################################################################################
# Choosing an Aperiodic Fitting Procedure
# ---------------------------------------
#
# It is important to choose the appropriate aperiodic fitting approach for your data.
#
# If there is a clear knee in the power spectrum, fitting in 'fixed' mode
# will not work well. However fitting FOOOF with knee fits may perform sub-optimally
# in ambiguous cases (where the data may or may not have a knee), or if no knee is present.
#
# Given this, we recommend:
#
# - Check your data, across the frequency range of interest,
#   for what the aperiodic signal looks like.
#
#   - If it looks roughly linear (in log-log space), fit without a knee.
#
#     - This is likely across smaller frequency ranges, such as 3-30.
#     - Do not perform no-knee fits across a range in which this does not hold.
#   - If there is a clear knee, then use knee fits.
#
#     - This is likely across larger fitting ranges such as 1-150 Hz.
# - Be wary of ambiguous ranges, where there may or may not be a knee.
#
#   - Trying to fit without a knee, when there is not a single consistent aperiodic signal,
#     can lead to very bad fits. But it is also a known issue that trying to fit with a knee
#     can lead to suboptimal fits when no knee is present.
#
#     - We therefore currently recommend picking frequency ranges in which the expected
#       aperiodic signal process is relatively clear.
#
