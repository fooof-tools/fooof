"""
Manipulating FOOOF Objects
==========================

Examples with combining, sub-selecting, and dropping FOOOF model fits.
"""

###################################################################################################
#
# For this example, we will again use simulated data, and explore manipulating FOOOF objects.
#

###################################################################################################

# Import FOOOF and FOOOFGroup objects and Bands object
from fooof import FOOOF, FOOOFGroup, Bands

# Import utility functions that manage & manipulate FOOOF objects
from fooof.objs.utils import average_fg, combine_fooofs, compare_info

# Import simulation functions to create our example data
from fooof.sim.gen import gen_power_spectrum
from fooof.sim.params import param_sampler

###################################################################################################
#
# First, we will simulate some example data, and fit some individual fits with FOOOF objects.
#

###################################################################################################

# Settings for simulations
freq_range = [1, 50]
freq_res = 0.25

# Create some example power spectra
freqs, powers_1 = gen_power_spectrum(freq_range, [0, 1.0], [10, 0.25, 2],
                                     nlv=0.00, freq_res=freq_res)
freqs, powers_2 = gen_power_spectrum(freq_range, [0, 1.2], [9, 0.20, 1.5],
                                     nlv=0.01, freq_res=freq_res)
freqs, powers_3 = gen_power_spectrum(freq_range, [0, 1.5], [11, 0.3, 2.5],
                                     nlv=0.02, freq_res=freq_res)

###################################################################################################

# Initialize a set of FOOOF objects
fm1, fm2, fm3 = FOOOF(max_n_peaks=4), FOOOF(max_n_peaks=4), FOOOF(max_n_peaks=4)

# Fit FOOOF models
fm1.fit(freqs, powers_1)
fm2.fit(freqs, powers_2)
fm3.fit(freqs, powers_3)

###################################################################################################
# Combining FOOOF Objects
# -----------------------
#
# Sometimes, when working with models in FOOOF or FOOOFGroup objects, you
# may want to combine them together, to check some group properties.
#
# The :func:`combine_fooofs` takes a list of FOOOF or FOOOFGroup objects,
# and combines all available fits together into a FOOOFGroup object.
#
# Let's now combine our individual model fits into a FOOOFGroup object.
#

###################################################################################################

# Combine FOOOF a list of FOOOF objects into a FOOOFGroup object
fg = combine_fooofs([fm1, fm2, fm3])

# Check the number of models in the object
#   Note that the length of a FOOOFGroup object is defined as the number of model fits
print('Number of model fits: ', len(fg))

###################################################################################################
# Note on Manipulating FOOOF Objects
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Note that these functions that manipulate FOOOF object typically do more than just
# copying result data - they also check and manage settings and meta-data of objects.
#
# For example, combining FOOOF objects returns a new FOOOF object with the same settings.
#
# We can see this by using the :func:`compare_info` function to compare the settings
# between FOOOF objects.
#
# You can also use this function if you wish to compare FOOOF objects to
# ensure that you are comparing model results that were fit with equivalent settings.
#

###################################################################################################

# Compare FOOOF objects for if they have the same settings
compare_info([fm1, fg], 'settings')

###################################################################################################
# Sub-Select from FOOOFGroup
# --------------------------
#
# When you have a FOOOFGroup object, you may also want to sub-select a group of models.
#
# Example use cases for this could be:
#
# - you want to sub-select models that meet some kind of goodness-of-fit criterion
# - you want to examine a subset of model reflect, for example, particular channels or trials
#
# To do so, we can use the :func:`get_group` method of the FOOOFGroup object.
# This method takes in the desired inputs, and returns a new FOOOFGroup object,
# containing only the requested model fits.
#
# Note that if you want to sub-select a single FOOOF model you can
# use the :func:`get_fooof`.
#

###################################################################################################

# Define indices of desired sub-selecting
#   This could be a 'region of interest', for example
inds = [0, 1]

# Sub-select our selection of models from the FOOOFGroup object
nfg = fg.get_group(inds)

# `nfg` is a new FOOOFGroup object
#   We can check how many models it contains
print('Number of model fits: ', len(nfg))

###################################################################################################
#
# From here, we could continue to do any analysis of interest on our new
# FOOOFGroup object, which contains only our models of interest.
#

###################################################################################################
# Dropping Fits from FOOOFGroup
# -----------------------------
#
# Another option is to 'drop' model fits from a FOOOFGroup object.
#
# This can be used, for example, for a quality control step. If you have checked through
# the object, and noticed some outlier model fits, you may want to exclude them from
# future analyses.
#
# In this case, we'll use an example in which we drop any model fits that
# have particularly high error.
#

###################################################################################################

# Drop all model fits above an error threshold
fg.drop(fg.get_params('error') > 0.01)

###################################################################################################
# Note on Dropped or Failed Fits
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# When models are dropped from FOOOFGroup objects, they are set as null models.
# They are therefore cleared of results, but not literally dropped, which
# is done to preserve the ordering of the FOOOFGroup, so that the `n-th` model
# doesn't change if some models are dropped.
#
# Note that there may in some cases be Null models in a FOOOFGroup without
# explicitly dropping them, if any models failed during the fitting process.
#

###################################################################################################

# Check information on null models (dropped models)
print('Number of Null models  : \t', fg.n_null_)
print('Indices of Null models : \t', fg.null_inds_)

# Despite the dropped model, the total number of models in the object is the same
#   This means that the indices are still the same as before dropping models
print('Number of model fits: ', len(fg))

###################################################################################################

# Null models are defined as all NaN (not a number)
for ind in fg.null_inds_:
    print(fg[ind])

###################################################################################################
# Note on Selecting From FOOOF Objects
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# For both `get_group` and `drop` that we have used above, these methods take
# an input of the indices of FOOOF model to select or drop. In both cases,
# the input can be defined in multiple ways, including directly indicating
# the indices as a list of integers, or boolean masks, as we used above.
#

###################################################################################################
# Averaging FOOOFGroup
# --------------------
#
# Finally, let's average across the models in our FOOOFGroup object, to examine
# the average model of the data.
#
# Note that in order to be able to average across individual models, we need to define
# a set of frequency bands to average peaks across. Otherwise, there is no clear way
# to average across all the peaks across all models.
#

###################################################################################################

# Define the periodic band regions to use to average across
#   Since our simulated data only had alpha peaks, we will only define alpha here
bands = Bands({'alpha': [7, 14]})

# Average across individual models fits, specifying bands and an averaging function
afm = average_fg(fg, bands, avg_method='median')

# Plot our average model of the data
afm.plot()
