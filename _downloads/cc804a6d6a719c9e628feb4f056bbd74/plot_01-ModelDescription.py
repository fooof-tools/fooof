"""
01: Model Description
=====================

A theoretical / mathematical description of the power spectrum model.
"""

###################################################################################################
# Introduction
# ------------
#
# Welcome to the tutorials!
#
# In this first tutorial, we will introduce a conceptual overview and mathematical
# description of power spectrum model, as well as visualizing some example models.
#
# Keep in mind as you go, that if you want more information that describes, motivates, and
# justifies our modeling approach, you can also check out the associated
# `paper <https://www.biorxiv.org/content/early/2018/04/11/299859>`_,
# and/or the
# `motivations <https://fooof-tools.github.io/fooof/auto_tutorials/index.html>`_
# section of the site.
#

###################################################################################################
# Example Power Spectra and Models
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# First, we will import and run some code to simulate some example power spectra, and
# fit some power spectrum models to them. These example data will be used throughout this
# tutorial, to visualize some data and the model.
#
# For the purpose of this tutorial, you don't need to know how this code works
# yet, and can skip past reading the code itself.
#

###################################################################################################

# Import required code for visualizing example models
from fooof import FOOOF
from fooof.sim import gen_power_spectrum
from fooof.plts.annotate import plot_annotated_model

###################################################################################################

# Simulate example power spectra
freqs1, powers1 = gen_power_spectrum([3, 40], [1, 1], [[10, 0.2, 1.25], [30, 0.15, 2]])
freqs2, powers2 = gen_power_spectrum([1, 150], [1, 125, 1.25],
                                     [[8, 0.15, 1.], [30, 0.1, 2]])

# Initialize a power spectrum models and fit the power spectra
fm1 = FOOOF(min_peak_height=0.05, verbose=False)
fm2 = FOOOF(min_peak_height=0.05, aperiodic_mode='knee', verbose=False)
fm1.fit(freqs1, powers1)
fm2.fit(freqs2, powers2)

###################################################################################################
# Conceptual Overview
# -------------------
#
# The goal of this module is to fit models to parameterize neural power spectra.
#
# One reason to do so is the idea that there are multiple distinct 'components' within
# neural field data. The goal of the model is therefore to measure these different#
# 'components' of the data.
#
# By components, we mean that we are going to conceptualize neural field data as consisting
# of a combination of aperiodic and periodic (oscillatory) activity. Restated, we could say
# that neural data contains both aperiodic and periodic components (or activity).
#
# The goal of the model is to measure these components, separately and explicitly,
# from frequency representations of neural field data (neural power spectra).
#

###################################################################################################
# Visualizing Power Spectrum Models
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# First, let's start with an example power spectrum, which already has a model fit to it.
#

###################################################################################################

# Plot an example power spectrum, with a model fit
fm1.plot(plot_peaks='shade', peak_kwargs={'color' : 'green'})

###################################################################################################
#
# In the plot above, we see a power spectrum in which there is a trend decreasing power
# across increasing frequencies. In some frequency regions, there is a 'peak' of power,
# over and above the general trend line across frequencies. These properties - power across
# all frequencies, with overlying peaks, we consider to be hallmarks of neural field data.
#
# More specifically, we can describe this spectrum in terms of its 'components':
#
# - `aperiodic`: activity, with no characteristic frequency (or 'non-frequency specific' activity)
#
#   - in power spectra, this looks like a line, or curve, across all frequencies
#   - in the plot above, this is what's captured by the dashed blue line
# - `periodic` : activity, with a characteristic frequency
#
#   - in power spectra, this looks like a 'peak', or 'bump', reflecting frequency specific power
#   - in the plot above, this is what's captured by the green shaded peaks
#
# Each of these components also has different 'features' or 'properties', that we can and
# want to describe and measure. Since these 'features' are things that we will be fitting in
# the model, we will call them `parameters` (as in, the 'model parameters').
#
# The full model of the power spectrum, in red, is the combination of the two components:
# the aperiodic component and the periodic component, which is the set of peaks.
#
# The goal of the model is to measure these two components, to create the full model
# fit, in a way that accurately and quantitatively describes the data, and in where the
# parameters fit in the model are useful and informative.
#

###################################################################################################
# Mathematical Description of Overall Model
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To enact the conceptual idea and description above, we will need to formalize the
# model described above. To do so, throughout this tutorial, we will lay out the mathematical
# description of how neural power spectra can be modeled as a combination of aperiodic
# and periodic activity.
#
# Broadly, the idea is to conceptualizing the power spectrum as:
#
# .. math::
#    NPS = AP + \sum_{n=0}^{N} P_n
#
# Where :math:`NPS` is a neural power spectrum, :math:`AP` is the aperiodic component,
# and each :math:`P_n` describes a peak, for :math:`N` peaks extracted from the power spectrum,
# which make up the periodic component.
#
# To fit this model, we need to describe :math:`AP` and :math:`P_n`. Each of these will be
# described in their own section, explaining the specific functions used to measure each
# component.
#

###################################################################################################
# Periodic Component
# ------------------
#
# By periodic activity, we mean activity that has a characteristic frequency.
# This includes what are typically referred to as neural oscillations, often described
# in particular frequency bands such as delta, theta, alpha, beta, gamma, etc.
#
# In the frequency domain, putative oscillations are frequency regions in which
# there are 'bumps' of power over and above the aperiodic component.
# We will generally refer to the these as 'peaks' in the neural power spectrum.
#
# To measure the periodic activity, we would like to describe these peaks, without our
# measures of these peaks being influenced by co-occurring aperiodic activity.
# This is important, since as we can see in the plots above, the aperiodic and periodic
# components of the data can 'overlap', in frequency space. This means the total power
# at a given frequency can have contributions from both components. To measure periodic power,
# specifically, we need to measure the power over and above the aperiodic component of the data.
#
# First let's explore an annotated version of our power spectrum model.
#

###################################################################################################

# Plot an annotated version of the power spectrum model
plot_annotated_model(fm1, annotate_aperiodic=False)

###################################################################################################
#
# In the labeled plot above, we can again see the different components of the model,
# as well as the labeled peak parameters.
#
# Note that vertical labels reflect parameters measured in the x-axis units, so in frequency,
# where as horizontal labels reflect parameters measured in y-axis units, so power.
#
# The periodic parameters are:
#
# - the `center frequency` of the peak, in units of frequency
# - the `power` of the peak, over the aperiodic component, in units of power
# - the `bandwidth`, or the width of the peak, units of frequency
#
# Wherever we detect a peak, these are the parameters that we will fit to the peak,
# to describe this component of the data.
#

###################################################################################################
# Mathematical Description of the Periodic Component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To fit these periodic components - the regions of power over above the aperiodic component,
# or 'peaks' - we use Gaussians.
#
# Each Gaussian, referred to as :math:`G_n`, is of the form:
#
# .. math::
#    G_n = a * exp (\frac{- (F - c)^2}{2 * w^2})
#
# This describes each peak in terms of parameters `a`, `c` and `w`, where:
#
# - :math:`a` is the height of the peak, over and above the aperiodic component
# - :math:`c` is the center frequency of the peak
# - :math:`w` is the width of the peak
# - :math:`F` is the vector of input frequencies
#

###################################################################################################
# Aperiodic Component
# -------------------
#
# By 'aperiodic' activity, we mean activity that is not rhythmic, or activity that has
# no characteristic frequency.
#
# In the power spectrum, we typically see this as 1/f-like activity, in which the power
# across frequencies decreases with a :math:`\frac{1}{F^\chi}` relationship.
#
# To measure the aperiodic activity, we would like to describe the pattern of activity
# across all frequencies, without our measure being influenced by any co-occurring periodic
# activity (peaks).
#

###################################################################################################

# Plot an annotated version of the power spectrum model
plot_annotated_model(fm1, annotate_peaks=False)

###################################################################################################
#
# The aperiodic parameters in the above plot are:
#
# - the `offset`, or overall up/down translation of the whole spectrum
# - the `exponent`, which describes the 'curve', or overall 'line' of the aperiodic component
#
# Note that diagonal labels are unit-less measures (in neither units of frequency of power).
#

###################################################################################################
# Mathematical Description of the Aperiodic Component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To fit the aperiodic component, we use an exponential function, which we
# will refer to as :math:`L`.
#
# Note that this function is fit on the semi-log power spectrum, meaning linear frequencies
# and :math:`log_{10}` power values. This is how we have been plotting so far.
#
# The exponential is of the form:
#
# .. math::
#    L = 10^b * \frac{1}{(k + F^\chi)}
#
# Or, equivalently:
#
# .. math::
#    L = b - \log(k + F^\chi)
#
# In this formulation, the parameters :math:`b`, :math:`k`, and :math:`\chi`
# define the aperiodic component, as:
#
# - :math:`b` is the broadband 'offset'
# - :math:`k` relates to the 'knee'
# - :math:`\chi` is the 'exponent' of the aperiodic fit
# - :math:`F` is the vector of input frequencies
#
# Note that fitting the knee parameter is optional. If used, the knee parameter defines a
# 'bend' in the aperiodic `1/f` like component of the data. If not used, the 'knee'
# parameter is set to zero.
#
# We use this exponential form, with the option of a knee, since though neural data is often
# discussed in terms of having `1/f` activity, across broader frequency ranges, there is
# typically not a single `1/f` characteristic. Using this form allows for modeling bends
# in the power spectrum of the aperiodic component, if and when they occur.
#

###################################################################################################
# A Note on Logging
# ~~~~~~~~~~~~~~~~~
#
# So far, we have been plotting in semi-log, meaning the x-axis (frequency) is in linear
# spacing, and the y-axis (power) is in log10 space. This is common practice, as power values
# are exponentially distributed.
#
# It can also be useful, for visualization, to plot with both axes on a log scale.
# Note that plotting in log-log is just a visualization choice, and does not affect
# how the data is stored and/or how models are fit.
#
# Below we can see the same spectrum again, with all the annotations on, plotted in log-log.
# The most notable difference, is that the aperiodic component is a straight line in log-log
# spacing. This is the hallmark of `1/f` activity.
#

###################################################################################################

# Plot the power spectrum model, in log-log space
plot_annotated_model(fm1, plt_log=True)

###################################################################################################
# Relating Exponents to Power Spectrum Slope
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Another way to measure 1/f properties in neural power spectra is to measure the slope
# of the spectrum in log-log spacing, fitting a linear equation as:
#
# .. math::
#    NPS = ax + b
#
# Where:
#
# - :math:`a` is the power spectrum slope
# - :math:`b` is the offset
#
# Since 1/f is a straight line in log-log spacing, this approach captures 1/f activity.
# This is equivalent to the exponential fits that we perform (when fitting with no knee).
#
# There is a direct relationship between the slope (:math:`a`)
# and the exponent (:math:`\chi`), which is:
#
# .. math::
#    \chi = -a
#

###################################################################################################
# Fitting Knees
# ~~~~~~~~~~~~~
#
# In the original model we fit and explored, there was no aperiodic 'knee'. Depending on
# the data, or the frequency range, there may or may not be a knee present in the data
# (more on that later in the tutorial).
#
# In the next plot, there is an annotated model, from a broader frequency range that also
# includes a knee. When plotted in log-log, the presence of a knee can be seen as 'bend' or
# 'knee' in the  aperiodic component.
#

###################################################################################################

# Plot an annotated version of the power spectrum model
plot_annotated_model(fm2, plt_log=True)

###################################################################################################
#
# The knee parameter fit to the model is a unit-less value that describes the curve of the
# aperiodic component (when plotted in log-log spacing). On the plot above, the annotation
# references the knee as the dot on the plot at the bend point.
#

###################################################################################################
# Conclusion
# ----------
#
# So far, we how explored the power spectrum model defined as a combination of the aperiodic
# fit, :math:`L` defined by the exponential fit, and the periodic component, which is comprised
# of `N` peaks, where each :math:`G_n` is fit with a Gaussian.
#
# In the next tutorial, we will start to use this model.
#
# For more technical details on the model formulation and fitting process, check out the
# `paper <https://www.biorxiv.org/content/early/2018/04/11/299859>`_.
#

###################################################################################################
#
# Sphinx settings:
# sphinx_gallery_thumbnail_number = 5
#
