"""Plots for aperiodic fits and parameters."""

from itertools import cycle

import numpy as np

from fooof.sim.gen import gen_freqs, gen_aperiodic
from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.style import check_n_style, style_param_plot
from fooof.plts.utils import check_ax, recursive_plot, check_plot_kwargs

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_aperiodic_params(aps, colors=None, labels=None,
                          ax=None, plot_style=style_param_plot, **plot_kwargs):
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
    plot_style : callable, optional, default: style_param_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['params']))

    if isinstance(aps, list):
        recursive_plot(aps, plot_aperiodic_params, ax, colors=colors, labels=labels,
                       plot_style=plot_style, **plot_kwargs)

    else:

        # Unpack data: offset as x; exponent as y
        xs, ys = aps[:, 0], aps[:, -1]
        sizes = plot_kwargs.pop('s', 150)

        plot_kwargs = check_plot_kwargs(plot_kwargs, {'alpha' : 0.7})
        ax.scatter(xs, ys, sizes, c=colors, label=labels, **plot_kwargs)

    # Add axis labels
    ax.set_xlabel('Offset')
    ax.set_ylabel('Exponent')

    check_n_style(plot_style, ax)


@check_dependency(plt, 'matplotlib')
def plot_aperiodic_fits(aps, freq_range, control_offset=False,
                        log_freqs=False, colors=None, labels=None,
                        ax=None, plot_style=style_param_plot, **plot_kwargs):
    """Plot reconstructions of model aperiodic fits.

    Parameters
    ----------
    aps : 2d array
        Aperiodic parameters. Each row is a parameter set, as [Off, Exp] or [Off, Knee, Exp].
    freq_range : list of [float, float]
        The frequency range to plot the peak fits across, as [f_min, f_max].
    control_offset : boolean, optonal, default: False
        Whether to control for the offset, by setting it to zero.
    log_freqs : boolean, optonal, default: False
        Whether to plot the x-axis in log space.
    colors : str or list of str, optional
        Color(s) to plot data.
    labels : list of str, optional
        Label(s) for plotted data, to be added in a legend.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_param_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['params']))

    if isinstance(aps, list):

        if not colors:
            colors = cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

        recursive_plot(aps, plot_function=plot_aperiodic_fits, ax=ax,
                       freq_range=tuple(freq_range),
                       control_offset=control_offset,
                       log_freqs=log_freqs, colors=colors, labels=labels,
                       plot_style=plot_style, **plot_kwargs)
    else:

        freqs = gen_freqs(freq_range, 0.1)
        plt_freqs = np.log10(freqs) if log_freqs else freqs

        colors = colors[0] if isinstance(colors, list) else colors

        avg_vals = np.zeros(shape=[len(freqs)])

        for ap_params in aps:

            if control_offset:

                # Copy the object to not overwrite any data
                ap_params = ap_params.copy()
                ap_params[0] = 0

            # Recreate & plot the aperiodic component from parameters
            ap_vals = gen_aperiodic(freqs, ap_params)

            plot_kwargs = check_plot_kwargs(plot_kwargs, {'alpha' : 0.35, 'linewidth' : 1.25})
            ax.plot(plt_freqs, ap_vals, color=colors, **plot_kwargs)

            # Collect a running average across components
            avg_vals = np.nansum(np.vstack([avg_vals, ap_vals]), axis=0)

        # Plot the average component
        avg = avg_vals / aps.shape[0]
        avg_color = 'black' if not colors else colors
        ax.plot(plt_freqs, avg, linewidth=plot_kwargs.get('linewidth')*3,
                color=avg_color, label=labels)

    # Add axis labels
    ax.set_xlabel('log(Frequency)' if log_freqs else 'Frequency')
    ax.set_ylabel('log(Power)')

    # Set plot limit
    ax.set_xlim(np.log10(freq_range) if log_freqs else freq_range)

    # Apply plot style
    check_n_style(plot_style, ax)
