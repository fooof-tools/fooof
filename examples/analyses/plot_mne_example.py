"""
Using fooof with MNE
====================

This examples illustrates how to use fooof with MNE and create topographical plots.

This tutorial does require that you have `MNE
<https://mne-tools.github.io/>`_ installed. If you don't already have
MNE, you can follow instructions to get it `here
<https://mne-tools.github.io/stable/getting_started.html>`_.
"""

###################################################################################################

# General imports
import numpy as np
import pandas as pd
from matplotlib import cm, colors, colorbar
import matplotlib.pyplot as plt

# Import MNE, as well as the MNE sample dataset
import mne
from mne import io
from mne.datasets import sample
from mne.viz import plot_topomap

# FOOOF imports
from fooof import FOOOF, FOOOFGroup
from fooof.analysis import *

###################################################################################################
# Load & Check MNE Data
# ---------------------
#
# First, we will load the example dataset from MNE, and have a quick look at the data.
#
# The MNE sample dataset is a combined MEG/EEG recording with an audiovisual task, as
# described `here <https://martinos.org/mne/stable/manual/sample_dataset.html>`_.
#
# For the current example, we are going to sub-select only the EEG data,
# and analyze it as continuous (non-epoched) data.
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

# Explicitly adding a default EEG average reference required for source localization
raw.set_eeg_reference()

###################################################################################################

# Plot the channel locations and labels
raw.plot_sensors(show_names=True)

###################################################################################################

# Creating epochs
reject = dict(eeg=180e-6)
event_id = {'left/auditory': 1}
events = mne.read_events(event_fname)
epochs = mne.Epochs(raw, events=events, event_id=event_id, tmin=5, tmax=125,
		    baseline=None, preload=True, verbose=False)

###################################################################################################

# Creating Power Spectra Densities
spectra, freqs = mne.time_frequency.psd_welch(epochs, fmin=1., fmax=50., n_fft=2000,
                                              n_overlap=250, n_per_seg=500)

###################################################################################################
# FOOOFGroup
# ----------
#
# The FOOOFGroup object is used to fit FOOOF models across the power spectra.
#

###################################################################################################

# Initialize a FOOOFGroup object, with desired settings
fg = FOOOFGroup(peak_width_limits=[1, 6], min_peak_height=0.075,
                max_n_peaks=6, peak_threshold=1, verbose=False)

###################################################################################################

# Selecting the first epoch of data to FOOOF
spectra = np.squeeze(spectra[0,:,:])
n_channels, n_freq = spectra.shape
num_blocks = len(mne.read_events(event_fname))

# Setting frequency range
freq_range = [3, 35]

# Fit the FOOOF model across all channels
fg.fit(freqs, spectra, freq_range)
fg.plot()

###################################################################################################

# Define labels for periodic & aperiodic features
feats = ["CFS", "PWS", "BWS"]
aperiodic_feats = ["Offset","Exponent"]

# Define bands of interest
bands = {'theta': [3, 7],
	 'alpha': [7, 14],
         'beta': [15, 30]}

# Create dictionaries to store all the periodic properties across frequencies
results = {}
for band_name in bands.keys():
    results[band_name] = np.zeros(shape=[num_blocks, n_channels, len(feats)])

# Creating dictionaries to store all the aperiodic properties across frequencies
exponent_results = np.zeros(shape=[num_blocks, n_channels, len(aperiodic_feats)])

###################################################################################################

# Populating periodic and aperiodic values
for block in range(0, num_blocks):
    for ind, res in enumerate(fg):
        exponent_results[block, ind, :] = res.aperiodic_params
        for band_label, band_range in bands.items():
            results[band_label][block, ind,  :] = get_band_peak(res.peak_params, band_range, True)

###################################################################################################
# Plotting Topographies
# ---------------------
#
# Now we can plot the extracted FOOOF features across all channels.
#

###################################################################################################

def plot_topo_colorbar(vmin, vmax, label):
    """Helper function to create colorbars for the topography plots."""

    fig = plt.figure(figsize=(2, 3))
    ax1 = fig.add_axes([0.9, 0.25, 0.15, 0.9])

    cmap = cm.viridis
    norm = colors.Normalize(vmin=vmin, vmax=vmax)

    cb1 = colorbar.ColorbarBase(plt.gca(), cmap=cmap,
                                norm=norm, orientation='vertical')

###################################################################################################
#
# In this example, we will be plotting the alpha center frequency and oscillatory exponent.

###################################################################################################

# Settings to grab the alpha center frequency
band = 'alpha'
cur_data = results[band]

topo_dat = np.mean(cur_data,0)

###################################################################################################

# Looking at the alpha center frequency
print('CURRENT FEATURE:', feats[0])
disp_dat = topo_dat[:,0]

inds = np.where(np.isnan(disp_dat))
disp_dat[inds] = np.nanmean(disp_dat)

vbuffer = 0.1 * (disp_dat.max() - disp_dat.min())
vmin, vmax,  = disp_dat.min() - vbuffer, disp_dat.max() + vbuffer

fig, ax = plt.subplots()
plot_topo_colorbar(vmin, vmax, feats[0])
mne.viz.plot_topomap(disp_dat, raw.info, vmin=vmin, vmax=vmax, cmap=cm.viridis, contours=0, axes=ax)

###################################################################################################

# Looking at the aperiodic exponent
cur_data = exponent_results

topo_dat = np.mean(cur_data,0)

print('CURRENT FEATURE:', aperiodic_feats[1])
disp_dat = topo_dat[:,1]

inds = np.where(np.isnan(disp_dat))
disp_dat[inds] = np.nanmean(disp_dat)

vbuffer = 0.1 * (disp_dat.max() - disp_dat.min())
vmin, vmax,  = disp_dat.min() - vbuffer, disp_dat.max() + vbuffer

fig, ax = plt.subplots()
plot_topo_colorbar(vmin, vmax, exponent_results[1])
mne.viz.plot_topomap(disp_dat, raw.info, vmin=vmin, vmax=vmax, cmap=cm.viridis, contours=0, axes=ax)
