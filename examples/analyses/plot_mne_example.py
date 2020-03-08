"""
Topographical Analyses with MNE
===============================

This examples illustrates how to use FOOOF with MNE, doing a topographical analysis.

This tutorial requires that you have `MNE <https://mne-tools.github.io/>`_
installed.

If you don't already have MNE, you can follow instructions to get it
`here <https://mne-tools.github.io/stable/getting_started.html>`_.

For this example, we will explore how to apply FOOOF to data loaded and managed with MNE,
and how to plot topographies of FOOOF outputs.
"""

###################################################################################################

# General imports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors, colorbar

# Import MNE, as well as the MNE sample dataset
import mne
from mne import io
from mne.datasets import sample
from mne.viz import plot_topomap
from mne.time_frequency import psd_welch

# FOOOF imports
from fooof import FOOOF, FOOOFGroup, Bands
from fooof.analysis import get_band_peak_fg
from fooof.plts.spectra import plot_spectrum

###################################################################################################
# Load & Check MNE Data
# ---------------------
#
# We will use the
# `MNE sample dataset <https://mne.tools/stable/overview/datasets_index.html?#sample>`_
# which is a combined MEG/EEG recording with an audiovisual task.
#
# First we will load the dataset from MNE, and have a quick look at the data,
# and extract the EEG data that we will use for the current example.
#
# Note that if you are running this locally, the following cell will download
# the example dataset, if you do not already have it.
#

###################################################################################################

# Get the data path for the MNE example data
raw_fname = sample.data_path() + '/MEG/sample/sample_audvis_filt-0-40_raw.fif'
event_fname = sample.data_path() + '/MEG/sample/sample_audvis_filt-0-40_raw-eve.fif'

# Load the file of example MNE data
raw = mne.io.read_raw_fif(raw_fname, preload=True, verbose=False)

###################################################################################################

# Select EEG channels from the dataset
raw = raw.pick_types(meg=False, eeg=True, eog=False, exclude='bads')

###################################################################################################

# Set the reference to be average reference
raw = raw.set_eeg_reference()

###################################################################################################
# Dealing with NaN Values
# -----------------------
#
# One thing to keep in mind when running FOOOF, and extracting bands of interest,
# is that there is no guarantee that FOOOF will detect peaks in any given range.
#
# This means that sometimes results for a given band can be NaN, which doesn't
# always work very well with further analyses that we may want to do.
#
# Keep in mind a that getting a NaN value for power in a particular band is different
# from canonical approaches, in which the power of a given frequency range is calculated,
# regardless if there is evidence of periodic power.
#
# To be able to deal with nan-values, we will define a helper function to
# check for nan values and apply policies to how to deal with them.
#

###################################################################################################

def check_nans(data, nan_policy='zero'):
    """Check an array for nan values, and replace, based on policy."""

    # Find where there are nan values in the data
    nan_inds = np.where(np.isnan(data))

    # Apply desired nan policy to data
    if nan_policy == 'zero':
        data[nan_inds] = 0
    elif nan_policy == 'mean':
        data[nan_inds] = np.nanmean(data)
    else:
        raise ValueError('Nan policy not understood.')

    return data

###################################################################################################
# Calculating Power Spectra
# -------------------------
#
# To fit FOOOF models, we need to convert the time-series data we have loaded in
# frequency representations - meaning we have to calculate power spectra.
#
# To do so, we will leverage the time frequency tools available with MNE,
# in the `time_frequency` module. In particular, we can use the :func:`psd_welch` function,
# that takes in MNE data objects and returns power spectra.
#

###################################################################################################

# Calculate power spectra across the whole data
spectra, freqs = psd_welch(raw, fmin=1, fmax=40, tmin=0, tmax=250,
                           n_overlap=150, n_fft=300)

###################################################################################################
# Calculating FOOOF Models
# ------------------------
#
# Now that we have power spectra, we can fit some FOOOF models.
#
# Since we have multiple power spectra, we will use the :obj:`FOOOFGroup` object.
#

###################################################################################################

# Initialize a FOOOFGroup object, with desired settings
fg = FOOOFGroup(peak_width_limits=[1, 6], min_peak_height=0.15,
                peak_threshold=2., max_n_peaks=6, verbose=False)

# Define the frequency range to fit
freq_range = [1, 30]

###################################################################################################

# Fit the FOOOF model across all channels
fg.fit(freqs, spectra, freq_range)

###################################################################################################

# Check the overall results of the group fits
fg.plot()

###################################################################################################
# Plotting Topographies
# ---------------------
#
# Now that we have our power spectrum models calculated across all channels,
# let's start by plotting topographies of some FOOOF features.
#
# To do so, we can leverage the fact that both MNE and FOOOF preserve data order.
# So, when we calculated power spectra, our output spectra kept the channel order
# that is described in the MNE data object, and so did our FOOOFGroup object.
#
# That means that to plot our topography, we can use the MNE :func:`plot_topomap`
# function, passing in extracted data for FOOOF features per channel, and
# using the MNE object to define the corresponding channel locations.
#

###################################################################################################
# Plotting Periodic Topographies
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Lets start start by plotting some periodic FOOOF features.
#
# To do so, we will use to :obj:`Bands` object to manage some band definitions,
# and some FOOOF analysis utilities to extracts peaks from bands of interest.
#

###################################################################################################

# Define frequency bands of interest
bands = Bands({'theta': [3, 7],
               'alpha': [7, 14],
               'beta': [15, 30]})

###################################################################################################

# Extract alpha peaks from the FOOOFGroup results
alphas = get_band_peak_fg(fg, bands.alpha)

# Extract the power values from the FOOOF peaks
alpha_pw = alphas[:, 1]

###################################################################################################

# Plot the topography of alpha power
plot_topomap(alpha_pw, raw.info, cmap=cm.viridis, contours=0);

###################################################################################################
#
# And there we have it, our FOOOFed alpha topography!
#
# The topography makes sense - we see a centro-posterior distribution of alpha power.
#
# Now we can extend this to plot the power of each of our other defined frequency bands.
#

###################################################################################################

# Plot the topographies across different frequency bands
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ind, (label, band_def) in enumerate(bands):

    # Get the power values across channels for the current band
    band_power = check_nans(get_band_peak_fg(fg, band_def)[:, 1])

    # Create a topomap for the current oscillation band
    mne.viz.plot_topomap(band_power, raw.info, cmap=cm.viridis, contours=0,
                         axes=axes[ind], show=False);

    # Set the plot title
    axes[ind].set_title(label + ' power', {'fontsize' : 20})

###################################################################################################
#
# You might notice that the topographies of oscillations bands other than alpha
# look a little 'patchy'. This is because we are setting any channels for which we
# did not find a peak as zero with our `check_nan` approach. Keep in mind also
# that this is a single subject analysis.
#

###################################################################################################
#
# Since we have the FOOOF models for each of our channels, we can also explore what
# these peaks look like in the underlying power spectrum models.
#
# Next, lets check the power spectra for the largest detected peaks within each band.
#

###################################################################################################

fig, axes = plt.subplots(1, 3, figsize=(15, 6))
for ind, (label, band_def) in enumerate(bands):

    # Get the power values across channels for the current band
    band_power = check_nans(get_band_peak_fg(fg, band_def)[:, 1])

    # Plot the extracted FOOOF model for the model with the most band power
    fg.get_fooof(np.argmax(band_power)).plot(ax=axes[ind], add_legend=False)

    # Set some plot aesthetics & plot title
    axes[ind].yaxis.set_ticklabels([])
    axes[ind].set_title('biggest ' + label + ' peak', {'fontsize' : 16})

###################################################################################################
# Plotting Aperiodic Topographies
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Next up, let's plot the topography of the aperiodic exponent.
#
# To do so, we can simply extract the aperiodic features from our FOOOF object,
# and plot them.
#

###################################################################################################

# Extract aperiodic exponent values from
exps = fg.get_params('aperiodic_params', 'exponent')

###################################################################################################

# The the topography of aperiodic exponents
plot_topomap(exps, raw.info, cmap=cm.viridis, contours=0)

###################################################################################################
#
# In the topography above, we can see that there is a fair amount of variation
# across the scalp in terms of aperiodic exponent value.
#
# To visualize how much the exponent values vary, we can plot channel power spectra,
# in this case extracting the highest and lower exponent values.
#

###################################################################################################

# Compare the power spectra between low and high exponent channels
fig, ax = plt.subplots(figsize=(8, 6))
plot_spectrum(fg.freqs, fg.get_fooof(np.argmin(exps)).power_spectrum,
              ax=ax, label='Low Exponent')
plot_spectrum(fg.freqs, fg.get_fooof(np.argmax(exps)).power_spectrum,
              ax=ax, label='High Exponent')

###################################################################################################
# Conclusion
# ----------
#
# In this example, we have seen how to apply FOOOF models to data that is managed
# and processed with MNE.
#

###################################################################################################
#
# Sphinx settings:
# sphinx_gallery_thumbnail_number = 2
#