"""
Aperiodic Parameters
====================

Exploring properties and topics related to aperiodic parameters.
"""

###################################################################################################

from scipy.stats import spearmanr

from fooof import FOOOF, FOOOFGroup
from fooof.plts.spectra import plot_spectra
from fooof.plts.annotate import plot_annotated_model
from fooof.plts.aperiodic import plot_aperiodic_params
from fooof.sim.params import Stepper, param_iter
from fooof.sim import gen_power_spectrum, gen_group_power_spectra
from fooof.utils.params import compute_time_constant, compute_knee_frequency

###################################################################################################
# 'Fixed' Model
# -------------
#
# First, we will explore the 'fixed' model, which fits an offset and exponent value
# to characterize the 1/f-like aperiodic component of the data.
#

###################################################################################################

# Simulate an example power spectrum
freqs, powers = gen_power_spectrum([1, 50], [0, 1], [10, 0.25, 2], freq_res=0.25)

###################################################################################################

# Initialize model object and fit power spectrum
fm = FOOOF(min_peak_height=0.1)
fm.fit(freqs, powers)

###################################################################################################

# Check the aperiodic parameters
fm.aperiodic_params_

###################################################################################################

# Plot annotated model of aperiodic parameters
plot_annotated_model(fm, annotate_peaks=False, annotate_aperiodic=True, plt_log=True)

###################################################################################################
# Comparing Offset & Exponent
# ---------------------------
#
# A common analysis of model fit parameters includes examining and comparing changes
# in the offset and/or exponent values of a set of models, which we will now explore.
#
# To do so, we will start by simulating a set of power spectra with different exponent values.
#

###################################################################################################

# Define simulation parameters, stepping across different exponent values
exp_steps = Stepper(0, 2, 0.25)
ap_params = param_iter([1, exp_steps])

###################################################################################################

# Simulate a group of power spectra
freqs, powers = gen_group_power_spectra(\
    len(exp_steps), [3, 40], ap_params, [10, 0.25, 1], freq_res=0.25, f_rotation=10)

###################################################################################################

# Plot the set of example power spectra
plot_spectra(freqs, powers, log_powers=True)

###################################################################################################

# Initialize a group mode object and parameterize the power spectra
fg = FOOOFGroup()
fg.fit(freqs, powers)

###################################################################################################

# Extract the aperiodic values of the model fits
ap_values = fg.get_params('aperiodic')

###################################################################################################

# Plot the aperiodic parameters
plot_aperiodic_params(fg.get_params('aperiodic'))

###################################################################################################

# Compute the correlation between the offset and exponent
spearmanr(ap_values[0, :], ap_values[1, :])

###################################################################################################
#
# What we see above matches the common finding that that the offset and exponent are
# often highly correlated! This is because if you imagine a change in exponent as
# the spectrum 'rotating' around some frequency value, then (almost) any change in exponent
# has a corresponding change in offset value! If you note in the above, we actually specified
# a rotation point around which the exponent changes.
#
# This can also be seen in this animation showing this effect across different rotation points:
#
# .. image:: https://raw.githubusercontent.com/fooof-tools/Visualizers/main/gifs/specrot.gif
#
# Notably this means that while the offset and exponent can change independently (there can be
# offset changes over and above exponent changes), the baseline expectation is that these
# two parameters are highly correlated and likely reflect the same change in the data!
#

###################################################################################################
# Knee Model
# ----------
#
# Next, let's explore the knee model, which parameterizes the aperiodic component with
# an offset, knee, and exponent value.
#

###################################################################################################

# Generate a power spectrum with a knee
freqs2, powers2 = gen_power_spectrum([1, 50], [0, 15, 1], [8, 0.125, 0.75], freq_res=0.25)

###################################################################################################

# Initialize model object and fit power spectrum
fm = FOOOF(min_peak_height=0.05, aperiodic_mode='knee')
fm.fit(freqs2, powers2)

###################################################################################################

# Plot annotated knee model
plot_annotated_model(fm, annotate_peaks=False, annotate_aperiodic=True, plt_log=True)

###################################################################################################

# Check the measured aperiodic parameters
fm.aperiodic_params_

###################################################################################################
# Knee Frequency
# ~~~~~~~~~~~~~~
#
# You might notice that the knee *parameter* is not an obvious value. Notably, this parameter
# value as extracted from the model is something of an abstract quantify based on the
# formalization of the underlying fit function. A more intuitive measure that we may
# be interested in is the 'knee frequency', which is an estimate of the frequency value
# at which the knee occurs.
#
# The :func:`~.compute_knee_frequency` function can be used to compute the knee frequency.
#

###################################################################################################

# Compute the knee frequency from aperiodic parameters
knee_frequency = compute_knee_frequency(*fm.aperiodic_params_[1:])
print('Knee frequency: ', knee_frequency)

###################################################################################################
# Time Constant
# ~~~~~~~~~~~~~
#
# Another interesting property of the knee parameter is that it has a direct relationship
# to the auto-correlation function, and from there to the empirical time constant of the data.
#
# The :func:`~.compute_time_constant` function can be used to compute the knee-derived
# time constant.
#

###################################################################################################

# Compute the characteristic time constant of a knee value
time_constant = compute_time_constant(fm.get_params('aperiodic', 'knee'))
print('Knee derived time constant: ', time_constant)
