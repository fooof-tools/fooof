"""
Manipulating FOOOF Objects
==========================

Examples with combining, sub-selecting, dropping, and averaging power spectrum models.
"""

###################################################################################################
#
# As you fit power spectrum models, you may end up with multiple FOOOF objects, as you fit
# models within and across subjects, conditions, trials, etc. To help manage and organize
# the potentially multiple FOOOF objects that can arise in these cases, here we will
# explore the utilities offered for managing and organizing within and between FOOOF
# objects.
#
# Using simulated data, in this example we will cover:
#
# - combining results across FOOOF objects
# - sub-selecting fits from FOOOFGroup objects
# - dropping specified model fits from FOOOFGroup objects
# - average across groups of FOOOF fits
#

###################################################################################################

# Import FOOOF & FOOOFGroup objects
from fooof import FOOOF

# Import Bands object, to manage frequency band definitions
from fooof.bands import Bands

# Import utility functions that manage & manipulate FOOOF objects
from fooof.objs.utils import average_fg, combine_fooofs, compare_info

# Import simulation functions to create our example data
from fooof.sim.gen import gen_power_spectrum

###################################################################################################
#
# First, we will simulate some example data, and fit some individual power spectrum models.
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

# Fit power spectrum models
fm1.fit(freqs, powers_1)
fm2.fit(freqs, powers_2)
fm3.fit(freqs, powers_3)

###################################################################################################
# Combining FOOOF Objects
# -----------------------
#
# Sometimes, when working with models in :class:`~fooof.FOOOF` or :class:`~fooof.FOOOFGroup`
# objects, you may want to combine them together, to check some group properties.
#
# The :func:`~.combine_fooofs` function takes a list of FOOOF and/or
# FOOOFGroup objects, and combines all available fits together into a FOOOFGroup object.
#
# Let's now combine our individual model fits into a FOOOFGroup object.
#

###################################################################################################

# Combine a list of FOOOF objects into a FOOOFGroup object
fg = combine_fooofs([fm1, fm2, fm3])

# Check the number of models in the object
#   Note that the length of a FOOOFGroup object is defined as the number of model fits
print('Number of model fits: ', len(fg))

###################################################################################################
# Note on Manipulating FOOOF Objects
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Note that these functions that manipulate FOOOF objects typically do more than just
# copy results data - they also check and manage settings and meta-data of objects.
#
# For example, combining FOOOF objects returns a new FOOOFGroup object with the same settings.
#
# We can see this by using the :func:`~.compare_info` function to compare
# the settings between FOOOF objects.
#
# You can also use this function if you wish to compare FOOOF objects to ensure that
# you are comparing model results that were fit with equivalent settings.
#

###################################################################################################

# Compare defined settings across FOOOF objects
compare_info([fm1, fg], 'settings')

###################################################################################################
# Sub-Select from FOOOFGroup
# --------------------------
#
# When you have a :class:`~fooof.FOOOFGroup` object, you may also want to sub-select
# a group of models.
#
# Example use cases for this could be:
#
# - you want to sub-select models that meet some kind of goodness-of-fit criterion
# - you want to examine a subset of model reflect, for example, particular channels or trials
#
# To do so, we can use the :func:`~fooof.FOOOFGroup.get_group` method of the FOOOFGroup object.
# This method takes in an input specifying which indices to sub-select, and returns a
# new FOOOFGroup object, containing only the requested model fits.
#
# Note that if you want to sub-select a single FOOOF model you can
# use the :meth:`~fooof.FOOOFGroup.get_fooof` method.
#

###################################################################################################

# Define indices of desired sub-selection of model fits
#   This could be a the indices for a 'region of interest', for example
inds = [0, 1]

# Sub-select our selection of models from the FOOOFGroup object
nfg = fg.get_group(inds)

# Check how many models our new FOOOFGroup object contains
print('Number of model fits: ', len(nfg))

###################################################################################################
#
# From here, we could continue to do any analyses of interest on our new
# FOOOFGroup object, which contains only our models of interest.
#

###################################################################################################
# Dropping Fits from FOOOFGroup
# -----------------------------
#
# Another option is to 'drop' model fits from a FOOOFGroup object. You can do this with
# the :meth:`~fooof.FOOOFGroup.drop` method from a :class:`~fooof.FOOOFGroup` object.
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
# When models are dropped from :class:`~fooof.FOOOFGroup` objects, they are set as null models.
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
# Both the :meth:`~fooof.FOOOFGroup.get_group` and :meth:`~fooof.FOOOFGroup.drop` methods
# take an input of the indices of FOOOF model to select or drop.
#
# In both cases, the input can be defined in multiple ways, including directly indicating
# the indices as a list of integers, or boolean masks.
#

###################################################################################################
# Averaging Across Model Fits
# ---------------------------
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
