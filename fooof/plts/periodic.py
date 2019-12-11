"""Plots for periodic fits and parameters."""

import numpy as np

from fooof.core.funcs import gaussian_function
from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.utils import check_ax, recursive_plot
from fooof.plts.settings import FIGSIZE_PARAMS
from fooof.plts.style import check_n_style, style_param_plot

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_peak_params(peaks, freq_range=None, colors=None, labels=None,
                     ax=None, plot_style=style_param_plot):
    """Plot peaks as dots representing center frequency, power and bandwidth.

    Parameters
    ----------
    peaks : 2d array or list of 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
    freq_range : list of [float, float] , optional
        The frequency range to plot the peak parameters across, as [f_min, f_max].
    colors : list of str, optional
        Color(s) to plot data.
    labels : list of str, optional
        Label(s) for plotted data, to be added in a legend.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    """

    ax = check_ax(ax, FIGSIZE_PARAMS)

    # If there is a list, use recurse function to loop across arrays of data and plot them
    if isinstance(peaks, list):
        recursive_plot(peaks, plot_peak_params, ax, colors=colors, labels=labels)

    # Otherwise, plot the array of data
    else:

        # Unpack data
        xs, ys = peaks[:, 0], peaks[:, 1]
        cs = peaks[:, 2]*150

        # Create the plot
        ax.scatter(xs, ys, cs, c=colors, alpha=0.7, label=labels)

    # Add axis labels
    ax.set_xlabel('Center Frequency (Hz)')
    ax.set_ylabel('Power')

    # Set plot limits
    if freq_range: ax.set_xlim(freq_range)
    ax.set_ylim([0, ax.get_ylim()[1]])

    check_n_style(plot_style, ax)


def plot_peak_fits(peaks, freq_range=None, ax=None, plot_style=style_param_plot):
    """Plot reconstructions of peak model fits.

    Parameters
    ----------
    peaks : 2d array
        Peak data. Each row is a peak, as [CF, PW, BW].
    freq_range : list of [float, float] , optional
        The frequency range to plot the peak fits across, as [f_min, f_max].
        If not provided, defaults to +/- 4 around given peak center frequencies.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    """

    ax = check_ax(ax, FIGSIZE_PARAMS)

    if not freq_range:

        # Set the frequency range to +/- a buffer, but don't let it drop below 0
        f_buffer = 4
        freq_range = [peaks[:, 0].min() - f_buffer if peaks[:, 0].min() - f_buffer > 0 else 0,
                      peaks[:, 0].max() + f_buffer]

    # Create the frequency axis, which will be the plot x-axis
    freqs = np.arange(*freq_range, 0.1)

    avg_vals = np.zeros(shape=[len(freqs)])
    for peak_params in peaks:

        # Create & plot the oscillation model from parameters
        peak_vals = gaussian_function(freqs, *peak_params)
        ax.plot(freqs, peak_vals, alpha=0.35, linewidth=1.5)

        # Collect a running average average peaks
        avg_vals = np.nansum(np.vstack([avg_vals, peak_vals]), axis=0)

    # Plot the average across all subjects
    avg = avg_vals / peaks.shape[0]
    ax.plot(freqs, avg, 'k', linewidth=3)

    # Add axis labels
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Power')

    # Set plot limits
    ax.set_xlim(freq_range)
    ax.set_ylim([0, ax.get_ylim()[1]])

    # Apply plot style
    check_n_style(plot_style, ax)
