"""Plot templates for the module.

Notes
-----
These are template plot structures for plots and/or reports.
They are not expected to be used directly by the user.
"""

from itertools import repeat, cycle

import numpy as np

from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.measures.properties import compute_average, compute_dispersion
from specparam.plts.utils import check_ax, set_alpha
from specparam.plts.settings import (PLT_FIGSIZES, DEFAULT_COLORS, PLT_TEXT_FONT,
                                     TITLE_FONTSIZE, LABEL_SIZE, TICK_LABELSIZE)

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_scatter_1(data, label=None, title=None, x_val=0, ax=None):
    """Plot a scatter plot, with a single y-axis.

    Parameters
    ----------
    data : 1d array
        Data to plot.
    label : str, optional
        Label for the data, to be set as the y-axis label.
    title : str, optional
        Title for the plot.
    x_val : int, optional, default: 0
        Position along the x-axis to plot set of data.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.

    Notes
    -----
    Data is jittered slightly, for visualization purposes (deviations on x-axis are meaningless).
    """

    ax = check_ax(ax)

    # Create x-axis data, with small jitter for visualization purposes
    x_data = np.ones_like(data) * x_val + np.random.normal(0, 0.025, data.shape)

    ax.scatter(x_data, data, s=36, alpha=set_alpha(len(data)))

    if label:
        ax.set_ylabel(label, fontsize=LABEL_SIZE)
        ax.set(xticks=[x_val], xticklabels=[label])

    if title:
        ax.set_title(title, fontsize=TITLE_FONTSIZE)

    ax.tick_params(axis='x', labelsize=TICK_LABELSIZE)
    ax.tick_params(axis='y', labelsize=TICK_LABELSIZE)

    ax.set_xlim([-0.5, 0.5])


@check_dependency(plt, 'matplotlib')
def plot_scatter_2(data_0, label_0, data_1, label_1, title=None, ax=None):
    """Plot a scatter plot, with two y-axes.

    Parameters
    ----------
    data_0 : 1d array
        Data to plot on the first axis.
    label_0 : str
        Label for the data on the first axis, to be set as the axis label.
    data_1 : 1d array
        Data to plot on the second axis.
    label_0 : str
        Label for the data on the second axis, to be set as the axis label.
    title : str, optional
        Title for the plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.

    Notes
    -----
    Data is jittered slightly, for visualization purposes (deviations on x-axis are meaningless).
    """

    ax = check_ax(ax)
    ax1 = ax.twinx()

    plot_scatter_1(data_0, label_0, ax=ax)
    plot_scatter_1(data_1, label_1, x_val=1, ax=ax1)

    if title:
        ax.set_title(title, fontsize=TITLE_FONTSIZE)

    ax.set(xlim=[-0.5, 1.5],
           xticks=[0, 1],
           xticklabels=[label_0, label_1])
    ax.tick_params(axis='x', labelsize=TICK_LABELSIZE)


@check_dependency(plt, 'matplotlib')
def plot_hist(data, label, title=None, n_bins=25, x_lims=None, ax=None):
    """Plot a histogram.

    Parameters
    ----------
    data : 1d array
        Data to plot.
    label : str
        Label for the data, to be set as the x-axis label.
    title : str, optional
        Title for the plot.
    n_bins : int, optional, default: 25
        Number of bins to use for the histogram.
    x_lims : list of float, optional
        Limits for the x-axis of the plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    ax = check_ax(ax)

    ax.hist(data[~np.isnan(data)], n_bins, range=x_lims, alpha=0.8)

    ax.set_xlabel(label, fontsize=LABEL_SIZE)
    ax.set_ylabel('Count', fontsize=LABEL_SIZE)

    if x_lims:
        ax.set_xlim(x_lims)

    if title:
        ax.set_title(title, fontsize=TITLE_FONTSIZE)

    ax.tick_params(axis='both', labelsize=TICK_LABELSIZE)


@check_dependency(plt, 'matplotlib')
def plot_yshade(x_vals, y_vals, average='mean', shade='std', scale=1., color=None,
                plot_function=None, ax=None, **plot_kwargs):
    """Create a plot with y-shading.

    Parameters
    ----------
    x_vals : 1d array
        Data values to be plotted on the x-axis.
    y_vals : 1d or 2d array
        Data values to be plotted on the y-axis. `shade` must be provided if 1d.
    average : 'mean', 'median' or callable, optional, default: 'mean'
        Averaging approach for plotting the average. Only used if y_vals is 2d.
        If set to None, no average line is plotted.
    shade : 'std', 'sem', 1d array or callable, optional, default: 'std'
        Approach for shading above/below the average.
        If set to None, no shading is plotted.
    scale : float, optional, default: 1.
        Factor to multiply the plotted shade by.
    color : str, optional, default: None
        Color to plot.
    plot_function : callable, optional
        Function to use to create the plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional keyword arguments to pass into the plot function.
    """

    ax = check_ax(ax)

    shade_alpha = plot_kwargs.pop('shade_alpha', 0.25)

    avg_data = compute_average(y_vals, average=average if average else 'mean')

    if average is not None:

        if plot_function:
            plot_function(x_vals, avg_data, color=color, ax=ax, **plot_kwargs)
        else:
            ax.plot(x_vals, avg_data, color=color, **plot_kwargs)

    if shade is not None:

        # Compute shade values, apply scaling & plot +/- y-shading
        shade_vals = compute_dispersion(y_vals, shade) * scale
        ax.fill_between(x_vals, avg_data - shade_vals, avg_data + shade_vals,
                        alpha=shade_alpha, color=color)


@check_dependency(plt, 'matplotlib')
def plot_param_over_time(times, param, label=None, title=None, add_legend=True, add_xlabel=True,
                         xlim=None, drop_xticks=False, ax=None, **plot_kwargs):
    """Plot a parameter over time.

    Parameters
    ----------
    times : 1d array
        Time indices, to be plotted on the x-axis.
        If set as None, the x-labels are set as window indices.
    param : 1d array
        Parameter values to plot.
    label : str, optional
        Label for the data, to be set as the y-axis label.
    add_legend : bool, optional, default: True
        Whether to add a legend to the plot.
    add_xlabel : bool, optional, default: True
        Whether to add an x-label to the plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional keyword arguments for the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['time']))

    if times is None:
        times = np.arange(0, len(param))

    ax.plot(times, param, label=label,
            alpha=plot_kwargs.pop('alpha', 0.8),
            **plot_kwargs)

    if add_xlabel:
        ax.set_xlabel('Time Window')
    ax.set_ylabel(label if label else 'Parameter Value')

    if drop_xticks:
        ax.set_xticks([], [])

    if xlim:
        ax.set_xlim(xlim)

    if label and add_legend:
        ax.legend(loc='upper left', framealpha=plot_kwargs.pop('legend_framealpha', 0.9))

    if title:
        ax.set_title(title)


@check_dependency(plt, 'matplotlib')
def plot_params_over_time(times, params, labels=None, title=None, colors=None,
                          ax=None, **plot_kwargs):
    """Plot multiple parameters over time.

    Parameters
    ----------
    times : 1d array
        Time indices, to be plotted on the x-axis.
        If set as None, the x-labels are set as window indices.
    params : list of 1d array
        Parameter values to plot.
    labels : list of str
        Label(s) for the data, to be set as the y-axis label(s).
    colors : list of str
        Color(s) to plot data.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional keyword arguments for the plot call.
    """

    labels = repeat(labels) if not isinstance(labels, list) else cycle(labels)
    colors = cycle(DEFAULT_COLORS) if not isinstance(colors, list) else cycle(colors)

    ax0 = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['time']))

    n_axes = len(params)
    axes = [ax0] + [ax0.twinx() for ind in range(n_axes-1)]

    if n_axes >= 3:
        for nax, ind in enumerate(range(2, n_axes)):
            axes[ind].spines.right.set_position(("axes", 1.1 + (.1 * nax)))

    for cax, cparams, label, color in zip(axes, params, labels, colors):
        plot_param_over_time(times, cparams, label, add_legend=False, color=color,
                             ax=cax, **plot_kwargs)

    if bool(labels):
        ax0.legend([cax.get_lines()[0] for cax in axes], labels,
                   loc='upper left', framealpha=plot_kwargs.pop('legend_framealpha', 0.9))

    if title:
        ax0.set_title(title, fontsize=14)

    # Puts the axis with the legend 'on top', while also making it transparent (to see others)
    ax0.set_zorder(1)
    ax0.patch.set_visible(False)


@check_dependency(plt, 'matplotlib')
def plot_param_over_time_yshade(times, param, average='nanmean', shade='nanstd', scale=1.,
                                color=None, ax=None, **plot_kwargs):
    """Plot parameter over time with y-axis shading.

    Parameters
    ----------
    times : 1d array
        Time indices, to be plotted on the x-axis.
        If set as None, the x-labels are set as window indices.
    param : 2d array
        Parameter values to plot, organized as [n_events, n_time_windows].
    average : 'mean', 'median' or callable, optional, default: 'mean'
        Averaging approach for plotting the average. Only used if y_vals is 2d.
    shade : 'std', 'sem', 1d array or callable, optional, default: 'std'
        Approach for shading above/below the average.
    scale : float, optional, default: 1.
        Factor to multiply the plotted shade by.
    color : str, optional, default: None
        Color to plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional keyword arguments for the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['time']))

    times = np.arange(0, param.shape[-1]) if times is None else times
    plot_yshade(times, param, average=average, shade=shade, scale=scale,
                color=color, plot_function=plot_param_over_time,
                ax=ax, **plot_kwargs)


@check_dependency(plt, 'matplotlib')
def plot_text(text, x, y, ax=None, **plot_kwargs):
    """Plot text.

    Parameters
    ----------
    text : str
        Text to plot.
    x, y : float
        The position to place the text.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional keyword arguments to pass into the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', None))

    ax.text(x, y, text, PLT_TEXT_FONT, ha='center', va='center', **plot_kwargs)
    ax.set_frame_on(False)
    ax.set(xticks=[], yticks=[])
