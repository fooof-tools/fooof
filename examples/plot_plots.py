"""
Plot Power Spectra
==================

Use the plots available with FOOOF.
"""

###################################################################################################

# Import FOOOF plotting functions
from fooof.plts.spectra import plot_spectrum, plot_spectra
from fooof.plts.spectra import plot_spectrum_shading, plot_spectra_shading

###################################################################################################

# Create a couple simulated power spectra to explore plotting with
#   Here we create two spectra, with different aperiodic components
#   but each with the same oscillations (a theta, alpha & beta)
from fooof.sim.gen import gen_group_power_spectra
fs, ps, _ = gen_group_power_spectra(2, [3, 40], [[0.75, 1.5], [0.25, 1]],
                                    [6, 0.2, 1, 10, 0.3, 1, 25, 0.15, 3])
ps1, ps2 = ps

###################################################################################################
# The FOOOF plotting module has plots for plotting single or multiple
# power spectra, options for plotting in linear or log space, and
# plots for shading frequency regions of interest.
#
# Plotting in FOOOF uses matplotlib. Plotting functions can also take in any
# matplotlib keyword arguments, that will be passed into the plot call.

###################################################################################################

# Create a spectrum plot with a single power spectrum
plot_spectrum(fs, ps2, log_powers=True)

###################################################################################################

# Plot multiple spectra on the same plot
plot_spectra(fs, ps, log_freqs=True, log_powers=True)

###################################################################################################

# Plot a single power spectrum, with a shaded region covering alpha
plot_spectrum_shading(fs, ps1, [8, 12], log_powers=True)

###################################################################################################

# Plot multiple power spectra, with shades covering theta & beta ranges
plot_spectra_shading(fs, ps, [[4, 8], [20, 30]], log_powers=True)
