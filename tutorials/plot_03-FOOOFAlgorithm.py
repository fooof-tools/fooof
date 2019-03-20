"""
03: FOOOF Algorithm
===================

A step by step overview of the FOOOF algorithm.

Note that this notebook is for demonstrative purposes, and does not
represent recommended usage of the FOOOF module.
"""

###################################################################################################
# Algorithmic Description
# -----------------------
#
# Briefly, the algorithm proceeds as such:
#
# - An initial fit of the aperiodic signal is taken across the power spectrum
# - This aperiodic fit is subtracted from the power spectrum, creating a flattened spectrum
# - Peaks are iteratively found in this flattened spectrum
# - A full peak fit is created of all peak candidates found
# - The peak fit is subtracted from the original power spectrum,
#   creating a peak-removed power spectrum
# - A final fit of the aperiodic signal is taken of the peak-removed power spectrum

###################################################################################################

# General imports
import numpy as np
import matplotlib.pyplot as plt

# Import the FOOOF object
from fooof import FOOOF

# Import a function to generate synthetic power spectra
from fooof.synth.gen import gen_aperiodic

# Import some internal functions from FOOOF
#  Note that these are used here for demonstration: - you do not need to import them to run FOOOF
from fooof.core.funcs import gaussian_function
from fooof.plts.spectra import plot_spectrum
from fooof.plts.fm import plot_peak_iter

###################################################################################################

# Set whether to plot in log-log space (used across the whole notebook)
plt_log = False

###################################################################################################

# Load example data
freqs = np.load('./dat/freqs_2.npy')
spectrum = np.load('./dat/spectrum_2.npy')

###################################################################################################

# Initialize a FOOOF object, with some settings
fm = FOOOF(peak_width_limits=[1, 8], max_n_peaks=6 , min_peak_height=0.15)

###################################################################################################
#
# Note that data can be added to FOOOF independent of fitting the model.
# You can then plot input data.
#

###################################################################################################

# Add data to FOOOF object
fm.add_data(freqs, spectrum, [3, 40])

###################################################################################################

# Plot the power spectrum that we just created
fm.plot(plt_log)

###################################################################################################
#
# The FOOOF object stores most of the intermediate steps internally.
#
# For this notebook, we will first fit the full model, as normal, but then step through,
# and visualize each step the algorithm takes to come to that final fit.
#

# Fit the FOOOF model
fm.fit(freqs, spectrum, [3, 40])

###################################################################################################

# Do an initial aperiodic signal fit - a robust fit, that excludes outliers
#  This recreates an initial fit that isn't ultimately stored in the FOOOF object)
init_ap_fit = gen_aperiodic(fm.freqs, fm._robust_ap_fit(fm.freqs, fm.power_spectrum))

# Plot the initial aperiodic fit
_, ax = plt.subplots(figsize=(12, 10))
plot_spectrum(fm.freqs, fm.power_spectrum, plt_log, label='Original Power Spectrum', ax=ax)
plot_spectrum(fm.freqs, init_ap_fit, plt_log, label='Initial Aperiodic Fit', ax=ax)

###################################################################################################
#
# The initial fit, as above, is used to create a flattened spectrum,
# from which peaks can be extracted.
#

###################################################################################################

# Flatten the power spectrum, by subtracting out the initial aperiodic fit
plot_spectrum(fm.freqs, fm._spectrum_flat, plt_log, label='Flattened Spectrum')

###################################################################################################
#
# With the flattened spectrum, FOOOF then initiates an iterative procedure to find peaks.
#
# For each iteration:
#
# - The maximum point of the flattened spectrum is found.
#
#   - If this point fails to pass the relative or absolute height threshold,
#     the procedure halts.
# - A Gaussian is fit around this maximum point
# - This 'guess' Gaussian is then subtracted from the flatted spectrum
# - The procedure continues to a new iteration with the new version of the flattend spectrum,
#   unless `max_n_peaks` has been reached
#

###################################################################################################

# Plot the iterative approach to finding peaks from the flattened spectrum
plot_peak_iter(fm)

###################################################################################################
#
# Once the iterative procedure has halted, the extracted 'guess' peaks,
# are then re-fit, all together, to the flattened spectrum, creating a peak fit.
#

###################################################################################################

# Fit gaussians to all candidate peaks together, and create peak fit
plot_spectrum(fm.freqs, fm._peak_fit, plt_log)

###################################################################################################
#
# This is now the peak component of the fit completed. This fit is then used to go
# back and try and get a better aperiodic fit.
#
# To do so, the peak fit is removed from the original power spectrum,
# leaving an 'aperiodic-only' spectrum for re-fitting.
#

###################################################################################################

# Create peak removed power spectrum (by removing peak fit from original spectrum)
plot_spectrum(fm.freqs, fm._spectrum_peak_rm, plt_log, label='Peak Removed Spectrum')

###################################################################################################

# Fit the final aperiodic fit on the peak removed power spectrum
_, ax = plt.subplots(figsize=(12, 10))
plot_spectrum(fm.freqs, fm._spectrum_peak_rm, plt_log, label='Peak Removed Spectrum', ax=ax)
plot_spectrum(fm.freqs, fm._ap_fit, plt_log, label='Final Aperiodic Fit', ax=ax)

###################################################################################################
# The aperiodic fit component of the model is now also complete.
# The two components can now be combined.
#

###################################################################################################

# Recreate the full FOOOF model, by combining the peak and aperiodic fits
plot_spectrum(fm.freqs, fm.fooofed_spectrum_, plt_log, label='Full Model')

###################################################################################################

# The last stage is to calculate the fit error, R^2, and update gaussian parameters -> peak parameters
#  These results are part of what are stored, and printed, as the model results
fm.print_results()

###################################################################################################

# Plot the full model fit of the power spectrum
#  The final fit (red), and aperiodic fit (blue), are the same as we plotted above
fm.plot(plt_log)
