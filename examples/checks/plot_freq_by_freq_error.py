"""
Frequency-by-Frequency Model Errors
===================================

Check the error of FOOOF models across frequencies.
"""

###################################################################################################

import numpy as np

from fooof import FOOOF, FOOOFGroup

from fooof.sim.gen import gen_power_spectrum, gen_group_power_spectra

from fooof.checks import compute_pointwise_error_fm, compute_pointwise_error_fg

###################################################################################################
# Checking the error of individual model fits
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Words, words words.
#

###################################################################################################

# Simulate an example power spectrum
fs, ps = gen_power_spectrum([3, 50], [1, 1], [10, 0.25, 0.5])

###################################################################################################

# Initialize a FOOOF model to fit with
fm = FOOOF(verbose=False)

# Parameterize our power spectrum
fm.fit(fs, ps)

###################################################################################################

# Calculate the error per frequency of the model
compute_pointwise_error_fm(fm, plot_errors=True)

###################################################################################################
#
# You can also calculate and return the frequency-by-frequency errors of a model fit.
#

###################################################################################################

#
errs_fm = compute_pointwise_error_fm(fm, plot_errors=False, return_errors=True)

###################################################################################################

# Note that
print('Average freq-by-freq error:\t {:1.3f}'.format(np.mean(errs_fm)))
print('FOOOF model fit error: \t\t {:1.3f}'.format(fm.error_))

###################################################################################################
# Checking the error across groups of model fits
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#

###################################################################################################

# Simulate a group of power spectra
fs, ps, _ = gen_group_power_spectra(10, [3, 50], [1, 1], [10, 0.3, 1], nlvs=0.1)

###################################################################################################

# Initialize a FOOOFGroup model to fit
fg = FOOOFGroup(min_peak_height=0.25, verbose=False)

###################################################################################################

# Parameterize our group of power spectra
fg.fit(fs, ps)

###################################################################################################
#
# Next, we can calculate
#

###################################################################################################

# Check the
#   In the group case, the sol
compute_pointwise_error_fg(fg, plot_errors=True)

###################################################################################################

errs_fg = compute_pointwise_error_fg(fg, False, True)

###################################################################################################

# Check
f_min_err = fg.freqs[np.argmin(np.mean(errs_fg, 0))]
f_min_std = fg.freqs[np.argmin(np.std(errs_fg, 0))]

###################################################################################################

print(f_min_err)
print(f_min_std)
