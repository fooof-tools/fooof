"""
Transforming Power Spectra
==========================

Apply transformations to power spectra.

One of the goals of parameterizing neural power spectra is to be able to understand
if and how power spectra may be different and/or be changing across time or context.

In order to explore how power spectra can change, the simulation framework also
provides functions and utilities for transforming power spectra. These approaches
can be useful to specifically define changes and how spectra relate to each other,
and track how outcome measures relate to changes in the power spectra.
"""

###################################################################################################

# Import the FOOOF object
from fooof import FOOOF

# Import simulation utilities to create example data
from fooof.sim.gen import gen_power_spectrum

# Import functions that can transform power spectra
from fooof.sim.transform import (rotate_spectrum, translate_spectrum,
                                 rotate_sim_spectrum, translate_sim_spectrum,
                                 compute_rotation_offset)

# Import plot function to visualize power spectra
from fooof.plts.spectra import plot_spectra

###################################################################################################

# Generate a simulated power spectrum
freqs, powers, params = gen_power_spectrum([3, 40], [1, 1], [10, 0.5, 1],
                                           return_params=True)

###################################################################################################
# Rotating Power Spectra
# ----------------------
#
# The :func:`rotate_spectrum` function takes in a power spectrum, and rotates the
# power spectrum a specified amount, around a specified frequency point, changing
# the aperiodic exponent of the spectrum.
#

###################################################################################################

# Rotation settings
delta_exp = 0.25        # How much to change the exponent by
f_rotation = 20         # The frequency at which to rotate the spectrum

# Rotate the power spectrum
r_powers = rotate_spectrum(freqs, powers, delta_exp, f_rotation)

###################################################################################################

# Plot the two power spectra, with the rotation applied
plot_spectra(freqs, [powers, r_powers], log_freqs=True, log_powers=True)

###################################################################################################
#
# Next, we can use FOOOF to check if our change in exponent went as expected.
#

###################################################################################################

# Initialize FOOOF models
fm1, fm2 = FOOOF(verbose=False), FOOOF(verbose=False)

# Fit FOOOF models to the original, and rotated, spectrum
fm1.fit(freqs, powers)
fm2.fit(freqs, r_powers)

# Check the measured exponent values
print("Original exponent value:\t {:1.2f}".format(\
    fm1.get_params('aperiodic_params', 'exponent')))
print("Rotated exponent value:\t{:1.2f}".format(\
    fm2.get_params('aperiodic_params', 'exponent')))

###################################################################################################
# Rotation Related Offset Changes
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Note that when you rotate a power spectrum, the offset also necessarily changes.
#
# If you wish to compute the change in offset that occurs due to a change in exponent,
# you can use the :func:`compute_rotation_offset` function.
#

###################################################################################################

# Calculate the change in offset from an exponent change
off_change = compute_rotation_offset(delta_exp, f_rotation)

# Check the change in offset
print("The induced change in offset is: \t {:1.2f}".format(off_change))

###################################################################################################
# Translating Power Spectra
# -------------------------
#
# Another transformation you can apply to power spectra is a translation, which changes
# the offset, effectively moving the whole spectrum up or down.
#
# Note that changing the offset does not change the exponent.
#

###################################################################################################

# Translation settings
delta_offset = 0.5        # How much to change the offset by

# Translate the power spectrum
t_powers = translate_spectrum(powers, delta_offset)

###################################################################################################

# Plot the two power spectra, with the translation applied
plot_spectra(freqs, [powers, t_powers], log_freqs=True, log_powers=True)

###################################################################################################
# Transforming while Tracking Simulation Parameters
# -------------------------------------------------
#
# As we've seen, transforming power spectra changes their definitions, and sometimes
# more than just the parameter we are manipulating directly.
#
# If you are transforming simulated spectra, it can be useful to keep track of these changes.
#
# To do so, there are also the function :func:`rotate_sim_spectrum` and
# :func:`translate_sim_spectrum`, which work the same as what we've seen so far, with
# the addition that they take in a :obj:`SimParams` object, and update and return a
# new :obj:`SimParams` object that tracks the updated simulation parameters.
#

###################################################################################################

# Rotate a power spectrum, tracking and updating simulation parameters
r_s_powers, r_params = rotate_sim_spectrum(freqs, powers, delta_exp, f_rotation, params)

# Check the updated sim params from after the rotation
print(r_params)

###################################################################################################

# Translate a power spectrum, tracking and updating simulation parameters
t_s_powers, t_params = translate_sim_spectrum(powers, delta_offset, params)

# Check the updated sim params from after the translation
print(t_params)
