"""Settings for plots."""

from collections import OrderedDict

from specparam.modutils.dependencies import safe_import

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

# Define list of default plot colors
DEFAULT_COLORS = plt.rcParams['axes.prop_cycle'].by_key()['color'] if plt else None

# Define default figure sizes
PLT_FIGSIZES = {'spectral' : (8.5, 6.5),
                'params' : (7, 6),
                'group' : (9, 7),
                'time' : (10, 2)}

# Define defaults for colors for plots, based on what is plotted
PLT_COLORS = {'data' : 'black',
              'periodic' : 'green',
              'aperiodic' : 'blue',
              'model' : 'red'}

# Define defaults for colors for parameters
PARAM_COLORS = {
    'offset' : '#19b6e6',
    'knee' : '#5f0e99',
    'exponent' : '#5325e8',
    'cf' : '#acc918',
    'pw' : '#28a103',
    'bw' : '#0fd197',
    'presence' : '#095407',
    'error' : '#940000',
    'r_squared' : '#ab7171',
}

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
AXIS_STYLE_ARGS = ['title', 'xlabel', 'ylabel', 'xlim', 'ylim',
                   'xticks', 'yticks', 'xticklabels', 'yticklabels']

# Line style arguments are those that can be defined on a line object
LINE_STYLE_ARGS = ['alpha', 'lw', 'linewidth', 'ls', 'linestyle',
                   'marker', 'ms', 'markersize']

# Collection style arguments are those that can be defined on a collections object
COLLECTION_STYLE_ARGS = ['alpha', 'edgecolor']

# Custom style arguments are those that are custom-handled by the plot style function
CUSTOM_STYLE_ARGS = ['title_fontsize', 'label_size', 'tick_labelsize',
                     'legend_size', 'legend_loc']

# Define list of available style functions - these can also be replaced by arguments
STYLERS = ['axis_styler', 'line_styler', 'collection_styler', 'custom_styler']

# Collect the full set of possible style related input keyword arguments
STYLE_ARGS = \
    AXIS_STYLE_ARGS + LINE_STYLE_ARGS + COLLECTION_STYLE_ARGS + CUSTOM_STYLE_ARGS + STYLERS

## Define default values for plot aesthetics
# These are all custom style arguments
TITLE_FONTSIZE = 18
LABEL_SIZE = 14
TICK_LABELSIZE = 12
LEGEND_SIZE = 12
LEGEND_LOC = 'best'

# Define default for plot text font
PLT_TEXT_FONT = {'family': 'monospace',
                 'weight': 'normal',
                 'size': 16}
