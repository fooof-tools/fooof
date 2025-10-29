"""
XX: Periodic Component Fitting
===============================

Choosing and using different modes for fitting the periodic component.
"""

###################################################################################################

# Import the model object
from specparam import SpectralModel

# Import a utility to download and load example data
from specparam.utils.download import load_example_data

###################################################################################################
# Periodic Fitting Approaches
# ---------------------------
#
# Words, words, words
#

###################################################################################################




###################################################################################################
# Mathematical Description of the Periodic Component
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# To fit this periodic activity - the regions of power over above the aperiodic component,
# or 'peaks' - the model uses Gaussians. As we've seen, there can be multiple peaks in the model.
#
# Each Gaussian, :math:`n`, referred to as :math:`G(F)_n`, is of the form:
#
# .. math::
#    G(F)_n = a * exp (\frac{- (F - c)^2}{2 * w^2})
#
# This describes each peak in terms of parameters `a`, `c` and `w`, where:
#
# - :math:`a` is the height of the peak, over and above the aperiodic component
# - :math:`c` is the center frequency of the peak
# - :math:`w` is the width of the peak
# - :math:`F` is the array of frequency values
#



###################################################################################################
# Notes on Interpreting Peak Parameters
# -------------------------------------
#
# Peak parameters are labeled as:
#
# - CF: center frequency of the extracted peak
# - PW: power of the peak, over and above the aperiodic component
# - BW: bandwidth of the extracted peak
#
# Note that the peak parameters that are returned are not exactly the same as the
# parameters of the Gaussians used internally to fit the peaks.
#
# Specifically:
#
# - CF is the exact same as mean parameter of the Gaussian
# - PW is the height of the model fit above the aperiodic component [1],
#   which is not necessarily the same as the Gaussian height
# - BW is 2 * the standard deviation of the Gaussian [2]
#
# [1] Since the Gaussians are fit together, if any Gaussians overlap,
# than the actual height of the fit at a given point can only be assessed
# when considering all Gaussians. To be better able to interpret heights
# for individual peaks, we re-define the peak height as above, and label it
# as 'power', as the units of the input data are expected to be units of power.
#
# [2] Gaussian standard deviation is '1 sided', where as the returned BW is '2 sided'.
#

###################################################################################################
#
# The underlying gaussian parameters are also available from the model object,
# in the ``gaussian_params_`` attribute.
#


###################################################################################################


###################################################################################################



###################################################################################################