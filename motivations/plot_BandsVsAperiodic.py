"""
Bands vs. Aperiodic
===================

Words, words, words.

"""

###################################################################################################
#
# Words, words, words.
#

###################################################################################################

import matplotlib.pyplot as plt

from fooof import FOOOF

from fooof.sim import gen_power_spectrum
from fooof.plts import plot_spectra, plot_spectra_shading

###################################################################################################
#
# Background Hypotheses
# ---------------------
#
# Prior reports have reported that, across development, there is a shift of (in adults, compared to kids):
# - decreased power in lower frequency bands (delta, theta)
# - increased power in higher frequency bands (beta, gamma)
# - an increase in alpha center frequency value
#
# This has typically been analyzed in distinct bands, as:
#
# - delta (1-4 Hz)
# - theta (4-8 Hz)
# - alpha (8-13 Hz)
# - beta (13-30 Hz)
# - gamma (30-48 Hz)
#
# Under this framework, there are multiple things changing, with correlated changes in power
# across 4 or 5 bands, and a shift in frequency in alpha.
#
# An alternative hypothesis is that what is actually changing between younger and older subjects
# is the aperiodic component, which reflects 1/f-like distributed activity across all frequencies.
# This change in 1/f, when analyzed in a band-by-band manner, looks like a series of changes across bands.

###################################################################################################

## Settings
# Define the band shade regions, and shade colours
shades = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 48]]
shade_cols = ['#e8dc35', '#46b870', '#1882d9',  '#a218d9', '#e60026']

# Initialize a FOOOF model to use
fm = FOOOF(verbose=False)


###################################################################################################
# Bands Model
# -----------
#
# Under this model, we posit that there are band specific changes in each band. To visualize this,
# we simulate hypothesized power spectra for adult and child subjects, with the same 1/f background,
# and varying overlying oscillation peaks.
#
# Note that in this visualization, for clarity, all band peak frequencies are simulated as the
# same between groups.
#
# There could also be shifts in center frequencies between groups.
#

###################################################################################################

# Set up the spectrum simulation definitions for old and yng groups
fs, old_spectrum_bands = gen_power_spectrum([1, 50], [1, 1],
                                            [[2, 0.25, 1], [6, 0.2, 1], [10, 0.5, 1.5], [20, 0.2, 3], [40, 0.25, 3.5]])
fs, yng_spectrum_bands = gen_power_spectrum([1, 50], [1, 1],
                                            [[2, 0.5, 1], [6, 0.3, 1], [10, 0.5, 1.5], [20, 0.15, 3], [40, 0.15, 3.5]])

###################################################################################################

# Plot the power spectra differences, under the bands model
plot_spectra_shading(fs, [old_spectrum_bands, yng_spectrum_bands], log_powers=True, linewidth=3,
                     shades=shades, shade_colors=shade_cols, labels=['Adults', 'Children'])
plt.xlim([1, 48]);
plt.title('Hypothesis - Bands Model', {'fontsize' : 24, 'fontweight' : 'bold'});

###################################################################################################
# Flatten the Spectra
# ~~~~~~~~~~~~~~~~~~~
#
# Under the bands model, controlling for 1/f activity and flattening the spectra should show
# specific differences in each band.
#
# It should also find no systematic difference in the 1/f between groups.
#

###################################################################################################

# Fit FOOOF models and use to measure 1/f and subtract it out from the spectra
fm.fit(fs, old_spectrum_bands)
old_bands_flat = fm.power_spectrum - fm._ap_fit
old_bands_sl = fm.get_params('aperiodic_params', 'exponent')
fm.fit(fs, yng_spectrum_bands)
yng_bands_flat = fm.power_spectrum - fm._ap_fit
yng_bands_sl = fm.get_params('aperiodic_params', 'exponent')

###################################################################################################

# Check the difference of 1/f between age groups
print('The difference of 1/f slope is: \t {:1.2f}'.format(old_bands_sl - yng_bands_sl))

###################################################################################################

# Plot the power spectra differences, under the bands model
plot_spectra_shading(fs, [old_bands_flat, yng_bands_flat], log_powers=False, linewidth=3,
                     shades=shades, shade_colors=shade_cols, labels=['Adults', 'Children'])
plt.xlim([1, 48]);
plt.title('Hypothesis - Flattened Bands Model', {'fontsize' : 24, 'fontweight' : 'bold'});

###################################################################################################
# Periodic & Aperiodic Model
# --------------------------
#
# An alternative possibility is that what is different between age groups is predominantly the 1/f.
#
# In this simulation, we simulate child and adult power spectra as having different 1/f properties.
#
# In this case, we have simulated an alpha oscillation, with a difference in peak frequency per group.
#
# Though there could also be oscillatory peaks in other bands, we note that these are not required to
# be present at all for there to be differences in power in different frequency regions reflecting
# different bands.
#

###################################################################################################

# Set up the spectrum simulation definitions for old and yng groups
fs, yng_spectrum_pam = gen_power_spectrum([1, 50], [1, 1.25], [9, 0.5, 1.5])
fs, old_spectrum_pam = gen_power_spectrum([1, 50], [0.7, 1], [10, 0.5, 1.5])

###################################################################################################

# Plot the power spectra differences, under the periodic and aperiodic model
plot_spectra_shading(fs, [old_spectrum_pam, yng_spectrum_pam], log_powers=True, linewidth=3,
                     shades=shades, shade_colors=shade_cols, labels=['Adults', 'Children'], log_freqs=False)
plt.xlim([1, 48]);
plt.title('Hypothesis - Flattened Periodic & Aperiodic Model', {'fontsize' : 24, 'fontweight' : 'bold'});

###################################################################################################
# Flatten the Spectra
# ~~~~~~~~~~~~~~~~~~~
#
# Under the PAM model, controlling for 1/f activity and flattening the spectra should show that
# there are not remaining differences in oscillation bands.

###################################################################################################

# Fit FOOOF models and use to measure 1/f and subtract it out from the spectra
fm.fit(fs, old_spectrum_pam)
old_pam_flat = fm.power_spectrum - fm._ap_fit
old_pam_sl = fm.get_params('aperiodic_params', 'exponent')

fm.fit(fs, yng_spectrum_pam)
yng_pam_flat = fm.power_spectrum - fm._ap_fit
yng_pam_sl = fm.get_params('aperiodic_params', 'exponent')

###################################################################################################

# Check the difference of 1/f between age groups
print('The difference of 1/f slope is: \t {:1.2f}'.format(old_pam_sl - yng_pam_sl))

###################################################################################################

# Plot the power spectra differences, under the bands model
plot_spectra_shading(fs, [old_pam_flat, yng_pam_flat], log_powers=False, linewidth=3,
                     shades=shades, shade_colors=shade_cols, labels=['Adults', 'Children'])
plt.xlim([1, 48]);
plt.title('Hypothesis - Bands Model', {'fontsize' : 24, 'fontweight' : 'bold'});

###################################################################################################
# Conclusion
# ----------
#
# The two models will give the same pattern of results when analyzing power within pre-specified
# frequency band ranges, when not doing anything to control for aperiodic or 1/f activity.
#
# However, when controlling for and measuring 1/f activity, and separating out oscillations
# (for example by using FOOOF), then the results will be different - with the PAM model suggesting
# that the main mode of difference will be in aperiodic parameters, as opposed to periodic ones.
#
