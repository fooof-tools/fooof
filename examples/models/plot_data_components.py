"""
Exploring Data Components
=========================

This example explores the different data components, exploring the isolated aperiodic
and periodic components as they are extracted from the data.
"""

###################################################################################################

# sphinx_gallery_thumbnail_number = 3

# Import FOOOF model objects
from fooof import FOOOF, FOOOFGroup

# Import function to plot power spectra
from fooof.plts.spectra import plot_spectra

# Import simulation functions to create some example data
from fooof.sim import gen_power_spectrum, gen_group_power_spectra

###################################################################################################

# Simulate example power spectrum
freqs, powers = gen_power_spectrum([1, 50], [0, 10, 1], [10, 0.25, 2], freq_res=0.25)

# Initialize model object and fit power spectrum
fm = FOOOF()
fm.fit(freqs, powers)

###################################################################################################
# Data Components
# ~~~~~~~~~~~~~~~
#
# The model fit process includes procedures for isolating aperiodic and periodic components in
# the data, fitting each of these components separately, and then combining the model components
# as the final fit (see the Tutorials for further details on these procedures).
#
# In doing this process, the model fit procedure computes and stores isolated data components,
# which are available in the model.
#
# Before diving into the isolated data components, let's check the data (`power_spectrum`)
# and full model fit of a model object (`fooofed_spectrum`).
#

###################################################################################################

# Plot the original power spectrum data from the object
plot_spectra(fm.freqs, fm.power_spectrum, color='black')

###################################################################################################

# Plot the power spectrum model from the object
plot_spectra(fm.freqs, fm.fooofed_spectrum_, color='red')

###################################################################################################
# Aperiodic Component
# ~~~~~~~~~~~~~~~~~~~
#
# To fit the aperiodic component, the model fit procedure includes a peak removal process.
#
# The resulting 'peak-removed' data component is stored in the model object, in the
# `_spectrum_peak_rm` attribute.
#

###################################################################################################

# Plot the peak removed spectrum data component
plot_spectra(fm.freqs, fm._spectrum_peak_rm, color='black')

###################################################################################################

# Plot the peak removed spectrum, with the model aperiodic fit
plot_spectra(fm.freqs, [fm._spectrum_peak_rm, fm._ap_fit],
             colors=['black', 'blue'], linestyle=['-', '--'])

###################################################################################################
# Periodic Component
# ~~~~~~~~~~~~~~~~~~
#
# To fit the periodic component, the model fit procedure removes the fit peaks from the power
# spectrum.
#
# The resulting 'flattened' data component is stored in the model object, in the
# `_spectrum_flat` attribute.
#

###################################################################################################

# Plot the flattened spectrum data component
plot_spectra(fm.freqs, fm._spectrum_flat, color='black')

###################################################################################################

# Plot the flattened spectrum data with the model peak fit
plot_spectra(fm.freqs, [fm._spectrum_flat, fm._peak_fit], colors=['black', 'green'])

###################################################################################################
# Full Model Fit
# ~~~~~~~~~~~~~~
#
# The full model fit, which we explored earlier, is calculated as the combination of the
# aperiodic and peak fit, which we can check by plotting these combined components.
#

###################################################################################################

# Plot the full model fit, as the combination of the aperiodic and peak model components
plot_spectra(fm.freqs, [fm._ap_fit + fm._peak_fit], color='red')

###################################################################################################
# Notes on Analyzing Data Components
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The above shows data components as they are available on the model object, and used in
# the fitting process. Some analyses may aim to use these isolated components to compute
# certain measures of interest on the data. Note that these data components are stored in
# 'private' attributes (indicated by a leading underscore), meaning in normal function they
# are not expected to be accessed by the user, but as we've seen above they can still be accessed.
# However, analyses derived from these isolated data components is not currently officially
# supported by the module, and so users who wish to do so should consider the benefits and
# limitations of any such analyses.
#
