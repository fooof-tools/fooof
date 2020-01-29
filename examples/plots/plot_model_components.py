"""
Plot Model Components
=====================

Explore the plots available to visualize FOOOF outputs.
"""

###################################################################################################

from fooof import FOOOFGroup

from fooof.bands import Bands
from fooof.analysis import get_band_peak_fg

from fooof.sim import gen_group_power_spectra
from fooof.sim.params import param_jitter

from fooof.plts.periodic import plot_peak_fits, plot_peak_params
from fooof.plts.aperiodic import plot_aperiodic_params, plot_aperiodic_fits

###################################################################################################
# Experiment Set Up & Simulate Data
# ---------------------------------
#
# For this example, we will simulate a potential experiment in which we compare
# FOOOF model components and parameters. For this experiment,  we will imagine
# we have one 'grand average' power spectrum per subject, and compare between two groups.
#
# Then, we will use the plots available through FOOOF to compare model components
# and parameters between these two groups.
#

###################################################################################################

# Set up labels and colors
colors = ['#2400a8', '#00700b']
labels = ['Group-1', 'Group-2']

###################################################################################################

# Set the number of 'subjects' per group
n_subjs = 20

# Define the frequency range for our simulations
freq_range = [1, 50]

# Define aperiodic parameters for each group, with some variation
g1_aps = param_jitter([1, 1.25], [0.5, 0.3])
g2_aps = param_jitter([1, 1.00], [0.5, 0.3])

# Define periodic parameters for each group, with some variation
g1_peaks = param_jitter([11, 1, 0.5], [0.5, 0.2, 0.2])
g2_peaks = param_jitter([9, 1, 0.5], [0.25, 0.1, 0.3])

###################################################################################################

# Simulate some test data
fs, ps1, _ = gen_group_power_spectra(n_subjs, freq_range, g1_aps, g1_peaks)
fs, ps2, _ = gen_group_power_spectra(n_subjs, freq_range, g2_aps, g2_peaks)

###################################################################################################
# Run FOOOF Analyses
# ~~~~~~~~~~~~~~~~~~
#
# Now that we have our simulated data, we can fit our data with FOOOF, using FOOOFGroup.
#

###################################################################################################

# Initialize FOOOFGroup for spectral parameterization
fg1 = FOOOFGroup(verbose=False)
fg2 = FOOOFGroup(verbose=False)

###################################################################################################

# Parameterize neural power spectra
fg1.fit(fs, ps1)
fg2.fit(fs, ps2)

###################################################################################################
# Periodic Components
# -------------------
#
# First, let's have a look at the periodic components.
#
# To do so, we will use the `Bands` object to store our frequency band definitions,
# which we can then use to sub-select peaks within bands of interest.
#
# We can then plot visualizations of the peak parameters, and the reconstructed fits.
#

###################################################################################################

# Define our bands of interest
bands = Bands({'theta' : [4, 8], 'alpha' :  [8, 13], 'beta' : [13, 30]})

###################################################################################################

# Extract alpha peaks from each group
g1_alphas = get_band_peak_fg(fg1, bands.alpha)
g2_alphas = get_band_peak_fg(fg2, bands.alpha)

###################################################################################################
# `plot_peak_params`
# ~~~~~~~~~~~~~~~~~~
#
# The `plot_peak_params` function takes in peak parameters, and visualizes them, as:
#
# - Center Frequency on the x-axis
# - Power on the y-axis
# - Bandwidth as the size of the circle
#

###################################################################################################

# Explore the peak parameters of Group 1's alphas
plot_peak_params(g1_alphas, freq_range=bands.alpha)

###################################################################################################

# Compare the peak parameters of alpha peaks between groups
plot_peak_params([g1_alphas, g2_alphas], freq_range=bands.alpha,
                 labels=labels, colors=colors)

###################################################################################################
# `plot_peak_fits`
# ~~~~~~~~~~~~~~~~
#
# The `plot_peak_fits` function takes in peak parameters, and reconstructs peak fits.
#

###################################################################################################

# Plot the peak fits of the alpha fits for Group 1
plot_peak_fits(g1_alphas)

###################################################################################################

# Compare the peak fits of alpha peaks between groups
plot_peak_fits([g1_alphas, g2_alphas],
               labels=labels, colors=colors)

###################################################################################################
# Aperiodic Parameters
# --------------------
#
# Next, let's have a look at the aperiodic components.
#

###################################################################################################

# Extract the aperiodic parameters for each group
aps1 = fg1.get_params('aperiodic_params')
aps2 = fg2.get_params('aperiodic_params')

###################################################################################################
# `plot_peak_params`
# ~~~~~~~~~~~~~~~~~~
#
# The `plot_aperiodic_params` function takes in aperiodic parameters, and visualizes them, as:
#
# - Offset on the x-axis
# - Exponent on the y-axis
#

###################################################################################################

# Plot the aperiodic parameters for Group 1
plot_aperiodic_params(aps1)

###################################################################################################

# Compare the aperiodic parameters between groups
plot_aperiodic_params([aps1, aps2], labels=labels, colors=colors)

###################################################################################################
# `plot_aperiodic_fits`
# ~~~~~~~~~~~~~~~~~~~~~
#
# The `plot_aperiodic_fits` function takes in aperiodic parameters,
# and reconstructs aperiodic fits.
#
# Here again we can plot visualizations of the peak parameters, and the reconstructed fits.
#

###################################################################################################

# Plot the aperiodic fits for Group 1
plot_aperiodic_fits(aps1, freq_range, control_offset=True)

###################################################################################################

# Plot the aperiodic fits for both groups Group 1
plot_aperiodic_fits([aps1, aps2], freq_range,
                    control_offset=True, log_freqs=True,
                    labels=labels, colors=colors)

###################################################################################################
# Conclusions
# -----------
#
# And there you have the plots available for visualizing and comparing model parameters and fits.
#
