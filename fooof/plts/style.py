"""Style and aesthetics definitions for plots."""

from itertools import cycle
from functools import wraps
import warnings

import matplotlib.pyplot as plt

from fooof.plts.settings import AXIS_STYLE_ARGS, LINE_STYLE_ARGS, CUSTOM_STYLE_ARGS, STYLE_ARGS
from fooof.plts.settings import (LABEL_SIZE, LEGEND_SIZE, LEGEND_LOC,
                                 TICK_LABELSIZE, TITLE_FONTSIZE)

###################################################################################################
###################################################################################################

def check_n_style(style_func, *args):
    """"Check if a style function has been passed, and apply it to a plot if so.

    Parameters
    ----------
    style_func : callable or None
        Function to apply styling to a plot axis.
    *args
        Inputs to the style plot.
    """

    if style_func:
        style_func(*args)


def style_spectrum_plot(ax, log_freqs, log_powers):
    """Apply style and aesthetics to a power spectrum plot.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply styling to.
    log_freqs : bool
        Whether the frequency axis is plotted in log space.
    log_powers : bool
        Whether the power axis is plotted in log space.
    """

    # Get labels, based on log status
    xlabel = 'Frequency' if not log_freqs else 'log(Frequency)'
    ylabel = 'Power' if not log_powers else 'log(Power)'

    # Aesthetics and axis labels
    ax.set_xlabel(xlabel, fontsize=20)
    ax.set_ylabel(ylabel, fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.grid(True)

    # If labels were provided, add a legend
    if ax.get_legend_handles_labels()[0]:
        ax.legend(prop={'size': 16}, loc='upper right')


def style_param_plot(ax):
    """Apply style and aesthetics to a peaks plot.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply styling to.
    """

    # Set the top and right side frame & ticks off
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Set linewidth of remaining spines
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    # Aesthetics and axis labels
    for item in ([ax.xaxis.label, ax.yaxis.label]):
        item.set_fontsize(20)
    ax.tick_params(axis='both', which='major', labelsize=16)

    # If labels were provided, add a legend and standardize the dot size
    if ax.get_legend_handles_labels()[0]:
        legend = ax.legend(prop={'size': 16})
        for handle in legend.legendHandles:
            handle._sizes = [100]


# Additional plot style customization

def apply_axis_style(ax, style_args=AXIS_STYLE_ARGS, **kwargs):
    """Apply axis plot style.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply style to.
    style_args : list of str
        A list of arguments to be sub-selected from `kwargs` and applied as axis styling.
    **kwargs
        Keyword arguments that define plot style to apply.
    """

    # Apply any provided axis style arguments
    plot_kwargs = {key : val for key, val in kwargs.items() if key in style_args}
    ax.set(**plot_kwargs)


def apply_plot_style(ax, style_args=LINE_STYLE_ARGS, **kwargs):
    """Apply line/scatter/histogram plot style.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply style to.
    style_args : list of str
        A list of arguments to be sub-selected from `kwargs` and applied as styling.
    **kwargs
        Keyword arguments that define style to apply.
    """

    # Get the plot object related styling arguments from the keyword arguments
    style_kwargs = {key : val for key, val in kwargs.items() if key in style_args}

    # For line plots
    if len(ax.lines) > 0:
        plot_objs = ax.lines

    # For scatter plots
    elif len(ax.collections) > 0:
        plot_objs = ax.collections

    # For histograms
    elif len(ax.patches) > 0:
        plot_objs = ax.patches

    # There is no styling to apply
    else:
        return

    plot_objs = [plot_objs] if not isinstance(plot_objs, list) else plot_objs

    # Apply any provided plot object style arguments
    for style, value in style_kwargs.items():

        # Values should be either a single value, for all plot objects, or a list, one  value per
        # object. This line checks type, and makes a cycle-able / loop-able object out of the values
        values = cycle([value] if isinstance(value, (int, float, str)) else value)

        # For line plots
        for plot_obj in plot_objs:
            plot_obj.set(**{style : next(values)})


def apply_custom_style(ax, **kwargs):
    """Apply custom plot style.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply style to.
    **kwargs
        Keyword arguments that define custom style to apply.
    """

    # If a title was provided, update the size
    if ax.get_title():
        ax.title.set_size(kwargs.pop('title_fontsize', TITLE_FONTSIZE))

    # Settings for the axis labels
    label_size = kwargs.pop('label_size', LABEL_SIZE)
    ax.xaxis.label.set_size(label_size)
    ax.yaxis.label.set_size(label_size)

    # Settings for the axis ticks
    ax.tick_params(axis='both', which='major',
                   labelsize=kwargs.pop('tick_labelsize', TICK_LABELSIZE))

    # If labels were provided, add a legend
    if ax.get_legend_handles_labels()[0]:
        ax.legend(prop={'size': kwargs.pop('legend_size', LEGEND_SIZE)},
                  loc=kwargs.pop('legend_loc', LEGEND_LOC))

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        plt.tight_layout()


def apply_style(ax, axis_styler=apply_axis_style, line_styler=apply_plot_style,
                custom_styler=apply_custom_style, **kwargs):
    """Apply plot style to a figure axis.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes to apply style to.
    axis_styler, line_styler, custom_styler : callable, optional
        Functions to apply style to aspects of the plot.
    **kwargs
        Keyword arguments that define style to apply.

    Notes
    -----
    This function wraps sub-functions which apply style to different plot elements.
    Each of these sub-functions can be replaced by passing in replacement callables.
    """

    axis_styler(ax, **kwargs)
    line_styler(ax, **kwargs)
    custom_styler(ax, **kwargs)


def style_plot(func, *args, **kwargs):
    """Decorator function to apply a plot style function, after plot generation.

    Parameters
    ----------
    func : callable
        The plotting function for creating a plot.
    *args, **kwargs
        Arguments & keyword arguments.
        These should include any arguments for the plot, and those for applying plot style.

    Notes
    -----
    This decorator works by:

    - catching all inputs that relate to plot style
    - creating a plot, using the passed in plotting function & passing in all non-style arguments
    - passing the style related arguments into a `apply_style` function which applies plot styling

    By default, this function applies styling with the `apply_style` function. Custom
    functions for applying style can be passed in using `apply_style` as a keyword argument.

    The `apply_style` function calls sub-functions for applying style different plot elements,
    and these sub-functions can be overridden by passing in alternatives for `axis_styler`,
    `line_styler`, and `custom_styler`.
    """

    @wraps(func)
    def decorated(*args, **kwargs):

        # Grab a custom style function, if provided, and grab any provided style arguments
        style_func = kwargs.pop('apply_style', apply_style)
        style_args = kwargs.pop('style_args', STYLE_ARGS)
        style_kwargs = {key : kwargs.pop(key) for key in style_args if key in kwargs}

        # Check how many lines are already on the plot, if it exists already
        n_lines_pre = len(kwargs['ax'].lines) if 'ax' in kwargs and kwargs['ax'] is not None else 0

        # Create the plot
        func(*args, **kwargs)

        # Get plot axis, if a specific one was provided, or if not, grab the current axis
        cur_ax = kwargs['ax'] if 'ax' in kwargs and kwargs['ax'] is not None else plt.gca()

        # Check how many lines were added to the plot, and make info available to plot styling
        n_lines_apply = len(cur_ax.lines) - n_lines_pre
        style_kwargs['n_lines_apply'] = n_lines_apply

        # Determine if styling should be applied to all axes
        all_axes = kwargs.pop('all_axes', False)
        cur_ax = plt.gcf().get_axes() if all_axes is True else cur_ax
        cur_ax = [cur_ax] if not isinstance(cur_ax, list) else cur_ax

        # Apply the styling function
        for ax in cur_ax:
            style_func(ax, **style_kwargs)

    return decorated
