"""
06: Metrics & Model Evaluation
==============================

An overview of metrics & model evaluation to examine model fit quality.
"""

###################################################################################################
# Model Metrics
# -------------
#
# In this tutorial, we will explore model metrics.
#
# The `specparam` module uses the term `metric` to refer to a measure that is computed that
# reflects something about the spectral model (but that is not computed as part of the model fit).
#
#

###################################################################################################
#
#
#

###################################################################################################
# Interpreting Model Fit Quality Measures
# ---------------------------------------
#
# After model fitting, some goodness of fit metrics are calculated to assist with assessing
# the quality of the model fits. It calculates both the model fit error, as the mean absolute
# error (MAE) between the full model fit (``modeled_spectrum_``) and the original power spectrum,
# as well as the R-squared correspondence between the original spectrum and the full model.
#

# These scores can be used to assess how the model is performing. However interpreting these
# measures requires a bit of nuance. Model fitting is NOT optimized to minimize fit error /
# maximize r-squared at all costs. To do so typically results in fitting a large number of peaks,
# in a way that overfits noise, and only artificially reduces error / maximizes r-squared.
#
# The power spectrum model is therefore tuned to try and measure the aperiodic component
# and peaks in a parsimonious manner, and, fit the `right` model (meaning the right aperiodic
# component and the right number of peaks) rather than the model with the lowest error.
#
# Given this, while high error / low r-squared may indicate a poor model fit, very low
# error / high r-squared may also indicate a power spectrum that is overfit, in particular
# in which the peak parameters from the model may reflect overfitting by fitting too many peaks.
#
# We therefore recommend that, for a given dataset, initial explorations should involve
# checking both cases in which model fit error is particularly large, as well as when it
# is particularly low. These explorations can be used to pick settings that are suitable
# for running across a group. There are not universal settings that optimize this, and so
# it is left up to the user to choose settings appropriately to not under- or over-fit
# for a given modality / dataset / application.
#


###################################################################################################


###################################################################################################


###################################################################################################
