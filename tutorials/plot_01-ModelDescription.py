"""
01: Model Description
=====================

A theoretical / mathematical description of the FOOOF model.
"""

###################################################################################################
# Introduction
# ------------
#
# Here we will first introduce a conceptual overview and mathematical description of
# the approach employed here to parameterize neural power spectra.
#
# If you wish to start with a more hands-on introduction of what the model looks like,
# you can skip ahead to the next tutorial, and come back here after.
#
# If you want more information that motivates and justifies our
# modeling approach, you can also check out the
# `associated paper <https://www.biorxiv.org/content/early/2018/04/11/299859>`_,
# and/or the
# `motivations section <https://fooof-tools.github.io/fooof/auto_tutorials/index.html>`_
# of the documentation site.
#

###################################################################################################
# Conceptual Overview
# -------------------
#
# The conceptual idea motivating the desire to parameterize neural power spectra is the
# idea that there are multiple distinct 'components' within neural field data,
# and we would like a way to explicitly and specifically model these different
# aspects of the data.
#
# More specifically, the FOOOF model conceptualizes the neural data as a combination
# of aperiodic and periodic (oscillatory) activity.
#
# The goal of the model is to measure these component, separately and explicitly,
# from frequency representations of neural field data (neural power spectra).
#

###################################################################################################
# Aperiodic Activity
# ~~~~~~~~~~~~~~~~~~
#
# By 'aperiodic' activity, we mean activity that is not rhythmic, or activity that has
# no characteristic frequency.
#
# In the power spectrum, we typically see this as 1/f-like activity, in which the power
# across frequencies decreases with a :math:`\frac{1}{F^\chi}` relationship.
#
# To measure the aperiodic activity, we would like to describe this activity,
# without our measure being influenced by any co-occurring periodic activity.
#

###################################################################################################
# Periodic Activity
# ~~~~~~~~~~~~~~~~~
#
# By periodic activity, we mean activity that does have a characteristic frequency.
# This includes what are typically referred to as neural oscillations, often described
# in particular frequency bands such as delta, theta, alpha, beta, gamma, etc.
#
# In the frequency domain, putative oscillations are frequency regions in which
# there are 'bumps' of power over and above the aperiodic component.
# We will generally refer to the these as 'peaks' in the neural power spectrum.
#
# To measure the periodic activity, we would like to describe these peaks, without our
# measures of these peaks being influenced by co-occurring aperiodic activity.
#

###################################################################################################
# Mathematical Overview
# ---------------------
#
# This formulation, of a combination of aperiodic and periodic activity,
# translates to conceptualizing the power spectrum as:
#
# .. math::
#    NPS = AP + \sum_{n=0}^{N} P_n
#
# Where :math:`NPS` is a neural power spectrum, :math:`AP` is the aperiodic component,
# and each :math:`P_n` describes a peak, for :math:`N` peaks extracted from the power spectrum,
# which makes up the periodic component.
#
# To enact this model, we need to describe how to measure :math:`AP` and :math:`P_n`,
# which we do next, by describing the specific functions we use to measure these components.
#

###################################################################################################
# Aperiodic Component
# ~~~~~~~~~~~~~~~~~~~
#
# To fit the aperiodic component, we use an exponential function,
# which we will refer to as :math:`L`.
# Note that this function is fit on the semi-log power spectrum
# (linear frequencies and :math:`log_{10}` power values).
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
# parameter is set to zero. Without a 'knee' parameter, this is equivalent to fitting
# a linear fit in log-log space to measure the 'slope' of the power spectrum (where the
# exponent = -slope).
#
# We use this form since though neural data is often discussed in terms of having
# `1/f` activity, across broader frequency ranges, there is typically not a single
# `1/f` characteristic. Using this form allows for modeling bends in the power spectrum
# of the aperiodic component, if and when they occur.
#

###################################################################################################
# Periodic Component(s)
# ~~~~~~~~~~~~~~~~~~~~~
#
# Regions of power over above the aperiodic component, or 'peaks', are considered to be
# putative oscillations, and form the periodic component(s) of the data. To fit these
# periodic components, we use Gaussians.
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
# Conclusion
# ----------
#
# The full power spectrum model is therefore the combination of the aperiodic fit,
# :math:`L` defined by the exponential fit, and `N` peaks, where each :math:`G_n`
# is fit with a Gaussian.
#
# The next tutorial, will start to use this model.
# For more technical details on the model formulation and fitting process, check out the
# `paper <https://www.biorxiv.org/content/early/2018/04/11/299859>`_,
#
