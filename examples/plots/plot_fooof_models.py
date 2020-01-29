"""
Plot Full FOOOF Models
======================

Words, words, words.
"""

###################################################################################################

import matplotlib.pyplot as plt

from fooof import FOOOF

from fooof.sim.gen import gen_power_spectrum, gen_group_power_spectra

###################################################################################################

# Generate an example power spectrum
fs, ps = gen_power_spectrum([3, 50], [1, 1],
                            [[9, 0.25, 0.5], [22, 0.1, 1.5], [25, 0.2, 1.]])

###################################################################################################

# Parameterize our simulated power spectrum
fm = FOOOF(verbose=False)
fm.fit(fs, ps)

###################################################################################################

# Plotting the Aperiodic Component
fm.plot(plot_aperiodic=True)

###################################################################################################

# Plotting Periodic Components
fig, axes = plt.subplots(2, 2, figsize=[16, 12])
peak_plots = ['shade', 'dot', 'outline', 'line']
for ax, peak_plot in zip(axes.flatten(), peak_plots):
    fm.plot(plot_peaks=peak_plot, add_legend=False, ax=ax)

###################################################################################################

# Combine peak representations
fm.plot(plot_aperiodic=True, plot_peaks='line-shade-outline', plt_log=False)

###################################################################################################
