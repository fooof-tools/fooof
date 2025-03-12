"""Plots for periodic fits and parameters."""

from itertools import cycle

import numpy as np

from specparam.sim import gen_freqs
from specparam.core.funcs import gaussian_function
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
def plot_peak_params(peaks, freq_range=None, colors=None, labels=None, ax=None, **plot_kwargs):
    """Plot peak parameters as dots representing center frequency, power and bandwidth.

    Parameters
    ----------
    peaks : 2d array or list of 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
    freq_range : list of [float, float] , optional
        The frequency range to plot the peak parameters across, as [f_min, f_max].
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

    # If there is a list, use recurse function to loop across arrays of data and plot them
    if isinstance(peaks, list):
        recursive_plot(peaks, plot_peak_params, ax, colors=colors, labels=labels)

    # Otherwise, plot the array of data
    else:

        # Unpack data: CF as x; PW as y; BW as size
        xs, ys = peaks[:, 0], peaks[:, 1]
        sizes = peaks[:, 2] * plot_kwargs.pop('s', 150)

        # Create the plot
        plot_kwargs = check_plot_kwargs(plot_kwargs, {'alpha' : 0.7})
        ax.scatter(xs, ys, sizes, c=colors, label=labels, **plot_kwargs)

    # Add axis labels
    ax.set_xlabel('Center Frequency')
    ax.set_ylabel('Power')

    # Set plot limits
    if freq_range:
        ax.set_xlim(freq_range)
    ax.set_ylim([0, ax.get_ylim()[1]])

    style_param_plot(ax)


@savefig
@style_plot
def plot_peak_fits(peaks, freq_range=None, average='mean', shade='sem', plot_individual=True,
                   colors=None, labels=None, ax=None, **plot_kwargs):
    """Plot reconstructions of model peak fits.

    Parameters
    ----------
    peaks : 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
    freq_range : list of [float, float] , optional
        The frequency range to plot the peak fits across, as [f_min, f_max].
        If not provided, defaults to +/- 4 around given peak center frequencies.
    average : {'mean', 'median'}, optional, default: 'mean'
        Approach to take to average across components.
        If set to None, no average is plotted.
    shade : {'sem', 'std'}, optional, default: 'sem'
        Approach for shading above/below the average reconstruction
        If set to None, no yshade is plotted.
    plot_individual : bool, optional, default: True
        Whether to plot individual component reconstructions.
        If False, only the average component reconstruction is plotted.
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

    if isinstance(peaks, list):

        if not colors:
            colors = cycle(plt.rcParams['axes.prop_cycle'].by_key()['color'])

        recursive_plot(peaks, plot_function=plot_peak_fits, ax=ax,
                       freq_range=tuple(freq_range) if freq_range else freq_range,
                       colors=colors, labels=labels, **plot_kwargs)

    else:

        if not freq_range:

            # Extract all the CF values, excluding any NaNs
            cfs = peaks[~np.isnan(peaks[:, 0]), 0]

            # Define the frequency range as +/- buffer around the data range
            #   This also doesn't let the plot range drop below 0
            f_buffer = 4
            freq_range = [cfs.min() - f_buffer if cfs.min() - f_buffer > 0 else 0,
                          cfs.max() + f_buffer]

        # Create the frequency axis, which will be the plot x-axis
        freqs = gen_freqs(freq_range, 0.1)

        colors = colors[0] if isinstance(colors, list) else colors

        all_peak_vals = np.zeros(shape=(len(peaks), len(freqs)))
        for ind, peak_params in enumerate(peaks):

            # Create & collect the peak model from parameters
            peak_vals = gaussian_function(freqs, *peak_params)
            all_peak_vals[ind, :] = peak_vals

            if plot_individual:
                ax.plot(freqs, peak_vals, color=colors, alpha=0.35, linewidth=1.25)

        # Plot the average across all components
        if average is not False:
            avg_color = 'black' if not colors else colors
            plot_yshade(freqs, all_peak_vals, average=average, shade=shade,
                        shade_alpha=plot_kwargs.pop('shade_alpha', 0.15),
                        color=avg_color, linewidth=3.75, label=labels, ax=ax)

    # Add axis labels
    ax.set_xlabel('Frequency')
    ax.set_ylabel('log(Power)')

    # Set plot limits
    ax.set_xlim(freq_range)
    ax.set_ylim([0, ax.get_ylim()[1]])

    # Apply plot style
    style_param_plot(ax)
