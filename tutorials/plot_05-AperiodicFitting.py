"""
05: Aperiodic Component Fitting
===============================

Choosing and using different modes for fitting the aperiodic component.
"""

###################################################################################################

# Import the FOOOF object
from fooof import FOOOF

# Import a utility to download and load example data
from fooof.utils.download import load_fooof_data

###################################################################################################
# Aperiodic Fitting Approaches
# ----------------------------
#
# There are currently two approaches for fitting the aperiodic component:
#
# - Fitting with just an offset and a exponent, equivalent to a linear fit in log-log space
#
#   - `aperiodic_mode` = 'fixed'
# - Including a 'knee' parameter, reflecting a fit with a bend, in log-log space
#
#   - `aperiodic_mode` = 'knee'
#
# Fitting in the 'fixed' mode assumes a single 1/f like characteristic to the aperiodic
# component, meaning it looks linear across all frequencies in log-log space.
#
# Though this assumption is true across *some* frequency ranges in neural data, it generally
# does not hold up across broad frequency ranges. If fitting is done in the 'fixed' mode,
# but the assumption of a single 1/f is violated, then fitting will go wrong.
#
# Broad frequency ranges (typically ranges greater than ~40 Hz range) typically do not
# have a single 1/f, as assumed by 'fixed' mode, as they typically exhibit a 'bend' in
# the aperiodic component. This indicates that there is not a single 1/f property across
# all frequencies, but rather a 'bend' in the aperiodic component. For these cases, fitting
# should be done using an extra parameter to capture this, using the 'knee' mode.
#

###################################################################################################
# Fitting with an Aperiodic 'Knee'
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Let's explore fitting power spectrum models across a broader frequency range,
# using some local field potential data.
#

###################################################################################################

# Load example data files needed for this example
freqs = load_fooof_data('freqs_lfp.npy', folder='data')
spectrum = load_fooof_data('spectrum_lfp.npy', folder='data')

###################################################################################################

# Initialize a FOOOF object, setting the aperiodic mode to use a 'knee' fit
fm = FOOOF(peak_width_limits=[2, 8], aperiodic_mode='knee')

###################################################################################################

# Fit a power spectrum model
#  Note that this time we're specifying an optional parameter to plot in log-log
fm.report(freqs, spectrum, [2, 70], plt_log=True)

###################################################################################################
# A note on interpreting the 'knee' parameter
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
# aperiodic component past the 'knee' inflecting point. Because of this, when doing knee fits,
# knee & exponent values should be considered together.
#

###################################################################################################
# Example: Aperiodic Fitting Gone Wrong
# -------------------------------------
#
# In the example above, we jumped directly to fitting with a knee.
#
# Here we will explore what it looks like if we don't use the appropriate mode for fitting
# the aperiodic component - fitting in 'fixed' mode when we should use 'knee'
#

###################################################################################################

# Create and fit a power spectrum model in fixed mode to the same data as above
fm = FOOOF(peak_width_limits=[2, 8], aperiodic_mode='fixed')
fm.report(freqs, spectrum, [2, 70], plt_log=True)

###################################################################################################
#
# In this case, we see that the 'fixed' aperiodic component (equivalent to a line
# in log-log space) is not able to capture the data, which has a curve.
#
# To compensate, the model adds extra peaks, but these are also not a good
# characterization of the data.
#
# In this example, the data, over this frequency range, needs to be fit in
# 'knee' mode to be able to appropriately characterize the data.
#

###################################################################################################
# Choosing an Aperiodic Fitting Procedure
# ---------------------------------------
#
# It is important to choose the appropriate aperiodic fitting approach for your data.
#
# If there is a clear knee in the power spectrum, fitting in 'fixed' mode will not
# work well. However fitting with a knee may perform sub-optimally in ambiguous cases
# (where the data may or may not have a knee), or if no knee is present.
#
# Given this, we recommend:
#
# - Check your data, across the frequency range of interest,
#   for what the aperiodic component looks like.
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
#   - Trying to fit without a knee, when there is not a single consistent aperiodic component,
#     can lead to very bad fits. However, trying to fit with a knee may lead to suboptimal fits
#     when no knee is present, and makes interpreting the exponent more difficult.
#
#     - We therefore currently recommend picking frequency ranges in which the expected
#       aperiodic component process is relatively clear.
#

###################################################################################################
# Conclusion
# ----------
#
# We have now explored the :class:`~fooof.FOOOF` object, and different fitting
# approaches for the aperiodic component. Next up, we will be introducing how
# to scale the fitting to apply across multiple power spectra.
#
