"""
Fit FOOOFGroup 3D
=================
"""

###################################################################################################
# This example shows how to run FOOOF across 3D matrices of power spectra
#

###################################################################################################

import numpy as np

# FOOOF imports
from fooof import FOOOFGroup
from fooof.funcs import fit_fooof_group_3d, combine_fooofs
from fooof.synth.gen import gen_group_power_spectra
from fooof.synth.params import param_sampler

###################################################################################################

# Settings for creating synthetic data
n_spectra = 10
freq_range = [3, 40]
ap_opts = param_sampler([[0, 1.0], [0, 1.5], [0, 2]])
gauss_opts = param_sampler([[], [10, 1, 1], [10, 1, 1, 20, 2, 1]])

###################################################################################################

# Generate some synthetic power spectra, and organize into a 3D matrix
spectra = []
for ind in range(3):
    fs, ps, _ = gen_group_power_spectra(n_spectra, freq_range, ap_opts, gauss_opts)
    spectra.append(ps)
spectra = np.array(spectra)

###################################################################################################

# Check the shape of the spectra
#   This kind of 3D organization can be thought to represent [n_conditions, n_channels, n_freqs]
print(spectra.shape)

###################################################################################################
# fit_fooof_group_3d
# ------------------
#
# The :func:`fit_fooof_group_3d` is a function that takes in a FOOOFGroup object,
# which has been initialized with the desired settings, as well as a frequency
# vector and a 3D matrix of power spectra. The FOOOFGroup object is used to fit
# FOOOF models across the power spectra. A list of FOOOFGroup objects is returned.
#

###################################################################################################

# Initialize a FOOOF group object, with desired settings
fg = FOOOFGroup(peak_width_limits=[1, 6], peak_threshold=0.5)

###################################################################################################

# Fit the 3D matrix of power spectra
fgs = fit_fooof_group_3d(fg, fs, spectra)

###################################################################################################

# This returns a list of FOOOFGRoup objects
print(fgs)

###################################################################################################

# Compare the aperiodic exponent results across conditions
for ind, fg in enumerate(fgs):
    print("Aperiodic exponent for condition {} is {:1.4f}".format(
        ind, np.mean(fg.get_all_data('aperiodic_params', 'exponent'))))

###################################################################################################
# combine_fooofs
# --------------
#
# Depending what the organization of the data is, you might also want to collapse
# FOOOF models dimensions that have been fit.
#
#
# To do so, you can use the :func:`combine_fooofs` function, which takes
# a list of FOOOF or FOOOFGroup objects, and combines them together into
# a single FOOOFGroup object (assuming the settings and data definitions
# are consistent to do so).

###################################################################################################

# You can also combine a list of FOOOF objects into a single FOOOF object
all_fg = combine_fooofs(fgs)

# Explore the results from across all FOOOF fits
all_fg.print_results()
all_fg.plot()
