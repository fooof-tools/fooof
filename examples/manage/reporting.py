"""
Reporting & Referencing
=======================

Example of model fit failures and how to debug them.
"""

###################################################################################################

# Import FOOOF model objects
from fooof import FOOOF, FOOOFGroup

#
from fooof.sim import gen_power_spectrum, gen_group_power_spectra

# Import utilities to print out information for reporting
from fooof.utils.reports import methods_report_info, methods_report_text

###################################################################################################
# Checking Module Version
# -----------------------
#
# Words, words, words.
#

###################################################################################################

# Check the version of the tool
from fooof import __version__ as fooof_version
print('Current fooof version:', fooof_version)

###################################################################################################
# Title
# -----
#
# Words, words, words.
#

###################################################################################################

# Initialize model object
fooof_obj = FOOOF()

###################################################################################################

# Print out all the methods information for reporting
methods_report_info(fooof_obj)

###################################################################################################

# Generate methods text, with methods information inserted
methods_report_text(fooof_obj)

###################################################################################################
# Title
# -----
#
# Words, words, words.
#

###################################################################################################

#
freqs, powers = gen_power_spectrum([1, 50], [0, 10, 1], [10, 0.25, 2], freq_res=0.25)

# Initialize model object
fm = FOOOF(min_peak_height=0.1, peak_width_limits=[1, 6], aperiodic_mode='knee')
fm.fit(freqs, powers)

###################################################################################################

# Generate methods text, with methods information inserted
methods_report_info(fm)

###################################################################################################

# Generate methods text, with methods information inserted
methods_report_text(fm)

###################################################################################################
# Title
# -----
#
# Words, words, words.
#

###################################################################################################

#
freqs, powers = gen_group_power_spectra(10, [1, 75], [0, 1], [10, 0.25, 2])

###################################################################################################

# Initialize and fit group model object
fg = FOOOFGroup(max_n_peaks=4, peak_threshold=1.75)
fg.fit(freq, powers)

###################################################################################################

# xx
methods_report_info(fg)

###################################################################################################

methods_report_text(fg)


###################################################################################################
#
# Words, words, words.
#