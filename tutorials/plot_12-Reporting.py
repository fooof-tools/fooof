"""
12: Reporting & Referencing
===========================

This section covers how to access reporting info and reference use of the module.

This page is a hands-on example of the reporting and referencing information on the
`Reference page <https://specparam-tools.github.io/reference.html>`_.
"""

###################################################################################################

# Import model objects
from specparam import SpectralModel, SpectralGroupModel

# Import simulation functions to create some example data
from specparam.sim import sim_power_spectrum, sim_group_power_spectra

# Import utilities to print out information for reporting
from specparam.reports.methods import methods_report_info, methods_report_text

# sphinx_gallery_start_ignore
# Note: this code gets hidden, but serves to create the text plot for the icon
from specparam.reports.strings import gen_methods_report_str
from specparam.plts.templates import plot_text
text = gen_methods_report_str()
plot_text(text, 0.5, 0.5, figsize=(12, 3))
# sphinx_gallery_end_ignore

###################################################################################################
# Checking Module Version
# -----------------------
#
# It's useful and important to keep track of which version of the module you are using,
# and to report this information when referencing use of the tool.
#
# There are several ways to check the version of the the module that you are using,
# including checking what is installed in the Python environment you are using.
#
# From within Python, you can also check the version of the module by checking
# `__version__`, as shown below:
#

###################################################################################################

# Check the version of the module
from specparam import __version__ as specparam_version
print('Current specparam version:', specparam_version)

###################################################################################################
# Getting Model Reporting Information
# -----------------------------------
#
# To assist with reporting information, the module has the following utilities:
#
# - the :func:`~.methods_report_info`, which prints out methods reporting information
# - the :func:`~.methods_report_text`, which prints out a template of methods reporting text
#
# Both of the these functions take as input a model object, and use the object to
# collect and return information related to the model fits.
#
# Note that not all information may be returned by the model - these methods only have access
# to the current object. This means it is also important that if you use these functions,
# you use them with objects that match the settings and data used in the analysis to be reported.
#
# In the following, we will explore an example of using these functions for an example model fit.
#

###################################################################################################

# Initialize model object
model = SpectralModel()

###################################################################################################

# Print out all the methods information for reporting
methods_report_info(model)

###################################################################################################
#
# You might notice that the above function prints out several different sections,
# some of which might look familiar.
#
# The settings information, for example, is the same as printed using the
# # - :meth:`~specparam.SpectralModel.print_settings` method.
#
# Next, let's check out the text version of the methods report.
#

###################################################################################################

# Generate methods text, with methods information inserted
methods_report_text(model)

###################################################################################################
# Additional Examples
# ~~~~~~~~~~~~~~~~~~~
#
# In the above examples, not all the information was printed, as not all information was
# available in the example object (for example, it had no data).
#
# In the next example, let's see how the outputs look for an example object with model fit results.
#

###################################################################################################

# Simulate an example power spectrum
freqs, powers = sim_power_spectrum(\
    [1, 50], {'knee' : [0, 10, 1]}, {'gaussian' : [10, 0.25, 2]}, freq_res=0.25)

# Initialize model object
fm = SpectralModel(min_peak_height=0.1, peak_width_limits=[1, 6], aperiodic_mode='knee')
fm.fit(freqs, powers)

###################################################################################################

# Generate methods text, with methods information inserted
methods_report_info(fm)

###################################################################################################

# Generate methods text, with methods information inserted
methods_report_text(fm)

###################################################################################################
#
# The report text is meant as a template / example that could be added to a methods section.
#
# Note that there may be missing information that needs to be filled in (indicated by 'XX's),
# and you can and should consider this a template to be edited as needed.
#

###################################################################################################
# Other Model Objects
# ~~~~~~~~~~~~~~~~~~~
#
# Note that the reporting functions work with any model object.
#
# For example, next we will use them on a :class:`~specparam.SpectralGroupModel` object.
#

###################################################################################################

# Simulate an example group of power spectra
freqs, powers = sim_group_power_spectra(\
    10, [1, 75], {'fixed' : [0, 1]}, {'gaussian' : [10, 0.25, 2]})

###################################################################################################

# Initialize and fit group model object
fg = SpectralGroupModel(max_n_peaks=4, peak_threshold=1.75)
fg.fit(freqs, powers)

###################################################################################################

# Generate the methods report information
methods_report_info(fg)

###################################################################################################

# Generate the methods report text
methods_report_text(fg)

###################################################################################################
#
# That concludes the example of using the helper utilities for generating methods reports!
#
