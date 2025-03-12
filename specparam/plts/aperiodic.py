"""Plots for aperiodic fits and parameters."""

from itertools import cycle

import numpy as np
import matplotlib.pyplot as plt

from specparam.sim.gen import gen_freqs, gen_aperiodic
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.plts.settings import PLT_FIGSIZES
from specparam.plts.templates import plot_yshade
from specparam.plts.style import style_param_plot, style_plot
from specparam.plts.utils import check_ax, recursive_plot, savefig, check_plot_kwargs

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_aperiodic_params(aps, colors=None, labels=None, ax=None, **plot_kwargs):
    """Plot aperiodic parameters as dots representing offset and exponent value.

    Parameters
    ----------
    aps : 2d array or list of 2d array
        Aperiodic parameters. Each row is a parameter set, as [Off, Exp] or [Off, Knee, Exp].
    colors : str or list of str, optional
        Color(s) to plot data.
    labels : list of str, optional
        Label(s) for plotted data, to be added in a legend.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['params']))

    if isinstance(aps, list):
        recursive_plot(aps, plot_aperiodic_params, ax, colors=colors, labels=labels)

    else:

        # Unpack data: offset as x; exponent as y
        xs, ys = aps[:, 0], aps[:, -1]
        sizes = plot_kwargs.pop('s', 150)

        # Create the plot
        plot_kwargs = check_plot_kwargs(plot_kwargs, {'alpha' : 0.7})
        ax.scatter(xs, ys, sizes, c=colors, label=labels, **plot_kwargs)

    # Add axis labels
    ax.set_xlabel('Offset')
    ax.set_ylabel('Exponent')

    style_param_plot(ax)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_aperiodic_fits(aps, freq_range, control_offset=False,
                        average='mean', shade='sem', plot_individual=True,
                        log_freqs=False, colors=None, labels=None,
                        ax=None, **plot_kwargs):
    """Plot reconstructions of model aperiodic fits.

    Parameters
    ----------
    aps : 2d array
        Aperiodic parameters. Each row is a parameter set, as [Off, Exp] or [Off, Knee, Exp].
    freq_range : list of [float, float]
        The frequency range to plot the peak fits across, as [f_min, f_max].
    average : {'mean', 'median'}, optional, default: 'mean'
        Approach to take to average across components.
        If set to None, no average is plotted.
    shade : {'sem', 'std'}, optional, default: 'sem'
        Approach for shading above/below the average reconstruction
        If set to None, no yshade is plotted.
    plot_individual : bool, optional, default: True
        Whether to plot individual component reconstructions.
        If False, only the average component reconstruction is plotted.
    control_offset : boolean, optional, default: False
        Whether to control for the offset, by setting it to zero.
    log_freqs : boolean, optional, default: False
        Whether to plot the x-axis in log space.
    colors : str or list of str, optional
        Color(s) to plot data.
    labels : list of str, optional
        Label(s) for plotted data, to be added in a legend.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['params']))

    if isinstance(aps, list):

        if not colors:
            colors = cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

        recursive_plot(aps, plot_aperiodic_fits, ax=ax, freq_range=tuple(freq_range),
                       control_offset=control_offset, log_freqs=log_freqs, colors=colors,
                       labels=labels, **plot_kwargs)
    else:

        freqs = gen_freqs(freq_range, 0.1)
        plt_freqs = np.log10(freqs) if log_freqs else freqs

        colors = colors[0] if isinstance(colors, list) else colors

        all_ap_vals = np.zeros(shape=(len(aps), len(freqs)))
        for ind, ap_params in enumerate(aps):

            if control_offset:

                # Copy the object to not overwrite any data
                ap_params = ap_params.copy()
                ap_params[0] = 0

            # Create & collect the aperiodic component model from parameters
            ap_vals = gen_aperiodic(freqs, ap_params)
            all_ap_vals[ind, :] = ap_vals

            if plot_individual:
                ax.plot(plt_freqs, ap_vals, color=colors, alpha=0.35, linewidth=1.25)

        # Plot the average across all components
        if average is not False:
            avg_color = 'black' if not colors else colors
            plot_yshade(freqs, all_ap_vals, average=average, shade=shade,
                        shade_alpha=plot_kwargs.pop('shade_alpha', 0.15),
                        color=avg_color, linewidth=3.75, label=labels, ax=ax)

    # Add axis labels
    ax.set_xlabel('log(Frequency)' if log_freqs else 'Frequency')
    ax.set_ylabel('log(Power)')

    # Set plot limit
    ax.set_xlim(np.log10(freq_range) if log_freqs else freq_range)

    style_param_plot(ax)
