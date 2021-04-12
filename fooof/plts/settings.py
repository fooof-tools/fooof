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

# Plot style arguments are those that can be defined on an axis object
AXIS_STYLE_ARGS = ['title', 'xlabel', 'ylabel', 'xlim', 'ylim']

# Line style arguments are those that can be defined on a line object
LINE_STYLE_ARGS = ['alpha', 'lw', 'linewidth', 'ls', 'linestyle',
                   'marker', 'ms', 'markersize']

# Collection style arguments are those that can be defined on a collections object
COLLECTION_STYLE_ARGS = ['alpha', 'edgecolor']

# Custom style arguments are those that are custom-handled by the plot style function
CUSTOM_STYLE_ARGS = ['title_fontsize', 'label_size', 'tick_labelsize',
                     'legend_size', 'legend_loc']
STYLERS = ['axis_styler', 'line_styler', 'custom_styler']
STYLE_ARGS = AXIS_STYLE_ARGS + LINE_STYLE_ARGS + CUSTOM_STYLE_ARGS + STYLERS

## Define default values for plot aesthetics
# These are all custom style arguments
TITLE_FONTSIZE = 20
LABEL_SIZE = 16
TICK_LABELSIZE = 16
LEGEND_SIZE = 12
LEGEND_LOC = 'best'
