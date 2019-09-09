"""Settings for plots."""

from collections import OrderedDict

###################################################################################################
###################################################################################################

# Default figure size
FIGSIZE_SPECTRAL = (12, 10)

# Levels for scaling alpha with the number of points in scatter plots
ALPHA_LEVELS = OrderedDict({0 : 0.50, 100  : 0.40, 500  : 0.25, 1000 : 0.10})
