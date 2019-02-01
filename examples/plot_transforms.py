"""
Transforming Power Spectra
==========================
"""

###################################################################################################
# This example covers transformations that can be applied to power spectra.
#

###################################################################################################

# Imports
from fooof.synth.gen import gen_power_spectrum
from fooof.synth.transform import rotate_spectrum

from fooof.plts.spectra import plot_spectra

###################################################################################################

# Generate a synthetic power spectrum
fs, ps = gen_power_spectrum([3, 40], [1, 1], [10, 0.5, 1])

###################################################################################################
# rotate_spectrum
# ---------------
#
# The :func:`rotate_spectrum` function takes in a power spectrum, and rotates the
# power spectrum a specified amount, around a specified frequency point, changing
# the aperiodic exponent of the spectrum.
#

###################################################################################################

# Rotate the power spectrum
nps = rotate_spectrum(fs, ps, 0.25, 20)

###################################################################################################

# Plot the two power spectra
plot_spectra(fs, [ps, nps], log_freqs=True, log_powers=True)
