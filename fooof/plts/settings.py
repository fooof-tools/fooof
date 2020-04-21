"""Settings for plots."""

from collections import OrderedDict

###################################################################################################
###################################################################################################

# Define default figure sizes
PLT_FIGSIZES = {'spectral' : (10, 8),
                'params' : (7, 6),
                'group' : (12, 10)}

# Define defaults for colors for plots, based on what is plotted
PLT_COLORS = {'data' : 'black',
              'periodic' : 'green',
              'aperiodic' : 'blue',
              'model' : 'red'}

# Levels for scaling alpha with the number of points in scatter plots
PLT_ALPHA_LEVELS = OrderedDict({0 : 0.50,
                                100 : 0.40,
                                500 : 0.25,
                                1000 : 0.10})

# Define a list of aliases for plot call inputs
PLT_ALIASES = {'linewidth' : ['lw', 'linewidth'],
               'markersize' : ['ms', 'markersize'],
               'linestyle' : ['ls', 'linestyle']}
