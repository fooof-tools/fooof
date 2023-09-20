"""
Exporting Model Results
=======================

This example covers utilities for extracting and exporting model fit results.

Note that the functionality to export to pandas DataFrames was added in version 1.1,
and requires the optional dependency `pandas` to be installed.
"""

###################################################################################################

# Import model objects, and Bands object to define bands of interest
from fooof import FOOOF, FOOOFGroup, Bands

# Import simulation functions to create some example data
from fooof.sim import gen_power_spectrum, gen_group_power_spectra

###################################################################################################
# Exporting Results
# -----------------
#
# In this example we will explore available functionality for extracting model fit results,
# specifically the options available for exporting results to pandas objects.
#
# Note that the main use case of exporting models to pandas DataFrames is for
# analysis across models. If you are just trying to access the model fit results from
# a fit model, you may want the :meth:`~fooof.FOOOF.get_results` and/or
# :meth:`~fooof.FOOOF.get_params` methods.
#
# Defining Oscillation Bands
# ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# A difficulty with exporting and collecting model results across model fits is that the
# models may be different sizes - most notably, they may contain different numbers of peaks.
#
# This means that we need to define some kind of strategy to organize the peak
# parameters across different models. Across these examples, this will include using the
# :class:`~fooof.Bands` object to define oscillations bands of interest.
#

###################################################################################################

# Initialize bands object, defining alpha band
bands1 = Bands({'alpha' : [7, 14]})

# Initialize model object
fm = FOOOF()

###################################################################################################

# Simulate example power spectrum
freqs, powers = gen_power_spectrum([1, 50], [0, 10, 1], [10, 0.25, 2], freq_res=0.25)

# Fit model to power spectrum
fm.fit(freqs, powers)

###################################################################################################
#
# The :meth:`~fooof.FOOOF.to_df` method supports exporting model fit results to pandas objects.
#

###################################################################################################

# Export results
fm.to_df(None)

###################################################################################################
#
# In the above, we export the model fit results to a pandas Series.
#
# Note that we explicitly passed in `None` to the `peak_org` argument, meaning we did not define
# a strategy for managing peaks. Because of this, the export did not include any peak parameters.
#
# Next, let's can try exporting again, this time passing in an integer to define the number
# of peaks to extract.
#

###################################################################################################

# Export results - extracting 1 peak
fm.to_df(1)

###################################################################################################
# Using Band Definitions
# ~~~~~~~~~~~~~~~~~~~~~~
#
# In the above, we extract the results specifying to extract 1 peak. By default, this approach
# will extract the dominant (highest power) peak.
#
# Notably, specifying a set number of peaks to extract does allow for combining across peaks
# (in terms of enforcing the same model size), but may not be the ideal way to examine across
# peaks (since the dominant extract peak may vary across model fits).
#
# Therefore, we may often want to instead define a set of band definitions to organize peaks,
# as can be done by passing a `Bands` object in to the `to_df` method.
#

###################################################################################################

# Export results - extracting peaks based on bands object
fm.to_df(bands1)

###################################################################################################
#
# Note that there are limitations to using the bands definitions - notably that doing so
# necessarily requires extracting at most 1 peak per band. In doing so, the extraction will
# select the dominant peak per band. However, this may not fully reflect the full model fit
# if there are, for example, multiple peaks fit within a band.
#

###################################################################################################
# Example on Group Object
# ~~~~~~~~~~~~~~~~~~~~~~~
#
# In the above, we used the model object to show the basic exporting functionalities.
#
# This functionality is more useful when considering multiple model fits together, such
# as can be done using the :meth:`~fooof.FOOOFGroup.to_df` method from the Group object,
# which allows for exporting DataFrames of organized model fit parameters across power spectra.
#
# As with the above, keep in mind that for some cases you may want the
# :meth:`~fooof.FOOOFGroup.get_results` and/or :meth:`~fooof.FOOOFGroup.get_params` methods
# instead of doing a DataFrame export.
#

###################################################################################################

# Simulate an example group of power spectra
freqs, powers = gen_group_power_spectra(5, [1, 50], [0, 1], [10, 0.25, 2])

# Initialize a group model object and fit power spectra
fg = FOOOFGroup(verbose=False)
fg.fit(freqs, powers)

###################################################################################################

# Export results to dataframe, with no peak definition
fg.to_df(None)

###################################################################################################

# Export results to dataframe, specifying to export a single peak
fg.to_df(1)

###################################################################################################

# Export results to dataframe, using bands definition with defines the alpha band
fg.to_df(bands1)

###################################################################################################
#
# In the above examples, we showed the same exports on the Group object as we previously
# explored on the single spectrum in the model object.
#
# Note that we can also define new bands objects to change the peak output organization,
# as demonstrated in the following example.
#

###################################################################################################

# Define a new bands object, specifying both the alpha and beta band
bands2 = Bands({'alpha' : [7, 14],
                'beta' : [15, 30]})

###################################################################################################

# Export results to dataframe, using bands object with alpha & beta
fg.to_df(bands2)

###################################################################################################
#
# That covers the pandas export functionality available from the model objects.
#
