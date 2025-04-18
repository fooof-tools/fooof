"""Power spectrum plotting functions.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from inspect import isfunction
from itertools import repeat, cycle

import numpy as np

from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.utils.select import dict_extract_keys
from specparam.plts.templates import plot_yshade
from specparam.plts.settings import PLT_FIGSIZES
from specparam.plts.style import style_spectrum_plot, style_plot
from specparam.plts.utils import check_ax, add_shades, savefig, check_plot_kwargs

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False, freq_range=None,
                 colors=None, labels=None, ax=None, **plot_kwargs):
    """Plot one or multiple power spectra.

    Parameters
    ----------
    freqs : 1d or 2d array or list of 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 1d or 2d array or list of 1d array
        Power values, to be plotted on the y-axis.
    log_freqs : bool, optional, default: False
        Whether to plot the frequency axis in log spacing.
    log_powers : bool, optional, default: False
        Whether to plot the power axis in log spacing.
    freq_range : list of [float, float], optional
        Frequency range to plot, defined in linear space.
    colors : list of str, optional, default: None
        Line colors of the spectra.
    labels : list of str, optional, default: None
        Legend labels for the spectra.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
        For spectra plots, boolean input `grid` can be used to control if the figure has a grid.
    """

    # Create the plot & collect plot kwargs of interest
    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))
    plot_kwargs = check_plot_kwargs(plot_kwargs, {'linewidth' : 2.0})
    grid = plot_kwargs.pop('grid', True)

    # Check for frequency range input, and log if x-axis is in log space
    if freq_range is not None:
        freq_range = np.log10(freq_range) if log_freqs else freq_range

    # Make inputs iterable if need to be passed multiple times to plot each spectrum
    plt_powers = np.reshape(power_spectra, (1, -1)) if isinstance(freqs, np.ndarray) and \
        np.ndim(power_spectra) == 1 else power_spectra
    plt_freqs = repeat(freqs) if isinstance(freqs, np.ndarray) and freqs.ndim == 1 else freqs

    # Set labels
    labels = plot_kwargs.pop('label') \
        if 'label' in plot_kwargs.keys() and labels is None else labels
    labels = repeat(labels) if not isinstance(labels, list) else cycle(labels)
    colors = repeat(colors) if not isinstance(colors, list) else cycle(colors)

    # Plot power spectra, looping across all spectra to plot
    for freqs, powers, color, label in zip(plt_freqs, plt_powers, colors, labels):

        # Set plot data, logging if requested, and collect color, if absent
        freqs = np.log10(freqs) if log_freqs else freqs
        powers = np.log10(powers) if log_powers else powers
        if color:
            plot_kwargs['color'] = color

        ax.plot(freqs, powers, label=label, **plot_kwargs)

    ax.set_xlim(freq_range)

    style_spectrum_plot(ax, log_freqs, log_powers, grid)


# Alias `plot_spectrum` to `plot_spectra` for backwards compatibility
plot_spectrum = plot_spectra


@savefig
@check_dependency(plt, 'matplotlib')
def plot_spectra_shading(freqs, power_spectra, shades, shade_colors='r',
                         add_center=False, ax=None, **plot_kwargs):
    """Plot one or multiple power spectra with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 1d or 2d array or list of 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 1d or 2d array or list of 1d array
        Power values, to be plotted on the y-axis.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    shade_colors : str or list of string
        Color(s) to plot shades.
    add_center : bool, optional, default: False
        Whether to add a line at the center point of the shaded regions.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
        For spectra plots, boolean input `grid` can be used to control if the figure has a grid.
        This can also include additional inputs into :func:`~.plot_spectra`.

    Notes
    -----
    Additional parameters for `plot_spectra` can also be provded as keyword arguments, including
    `log_freqs`, `log_powers` & `labels`. See `plot_spectra` for usage details.

    Additional keyword arguments can be passed to manage the shade styling, including
    'shade_alpha' and 'center_alpha'. See `add_shades` for usage details.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    shade_kwargs = dict_extract_keys(plot_kwargs, ['shade_alpha', 'center_alpha'])

    plot_spectra(freqs, power_spectra, ax=ax, **plot_kwargs)

    add_shades(ax, shades, shade_colors, add_center=add_center,
               logged=plot_kwargs.get('log_freqs', False), **shade_kwargs)

    style_spectrum_plot(ax, plot_kwargs.get('log_freqs', False),
                        plot_kwargs.get('log_powers', False),
                        plot_kwargs.get('grid', True))


# Alias `plot_spectrum_shading` to `plot_spectra_shading` for backwards compatibility
plot_spectrum_shading = plot_spectra_shading


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectra_yshade(freqs, power_spectra, average='mean', shade='std', scale=1,
                        log_freqs=False, log_powers=False, color=None, label=None,
                        ax=None, **plot_kwargs):
    """Plot standard deviation or error as a shaded region around the mean spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 1d or 2d array
        Power values, to be plotted on the y-axis. ``shade`` must be provided if 1d.
    average : 'mean', 'median' or callable, optional, default: 'mean'
        Averaging approach for the average spectrum to plot. Only used if power_spectra is 2d.
    shade : 'std', 'sem', 1d array or callable, optional, default: 'std'
        Approach for shading above/below the mean spectrum.
    scale : int, optional, default: 1
        Factor to multiply the plotted shade by.
    log_freqs : bool, optional, default: False
        Whether to plot the frequency axis in log spacing.
    log_powers : bool, optional, default: False
        Whether to plot the power axis in log spacing.
    color : str, optional, default: None
        Line color of the spectrum.
    label : str, optional, default: None
        Legend label for the spectrum.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
        For spectra plots, boolean input `grid` can be used to control if the figure has a grid.
        This can also include additional inputs into :func:`~.plot_spectra`.
    """

    if (isinstance(shade, str) or isfunction(shade)) and power_spectra.ndim != 2:
        raise ValueError('Power spectra must be 2d if shade is not given.')

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))
    grid = plot_kwargs.pop('grid', True)

    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectra) if log_powers else power_spectra

    plot_yshade(plt_freqs, plt_powers, average=average, shade=shade, scale=scale,
                color=color, label=label, plot_function=plot_spectra,
                ax=ax, **plot_kwargs)

    style_spectrum_plot(ax, log_freqs, log_powers, grid)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectrogram(freqs, powers, times=None, **plot_kwargs):
    """Plot a spectrogram.

    Parameters
    ----------
    freqs : 1d array
        Frequency values.
    powers : 2d array
        Power values for the spectrogram, organized as [n_frequencies, n_time_windows].
    times : 1d array, optional
        Time values for the time windows.
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.
    """

    _, ax = plt.subplots(figsize=(12, 6))

    n_freqs, n_times = powers.shape

    ax.imshow(powers, origin='lower', **plot_kwargs)

    ax.set(yticks=np.arange(0, n_freqs, 1)[freqs % 5 == 0],
           yticklabels=freqs[freqs % 5 == 0])

    if times is not None:
        ax.set(xticks=np.arange(0, n_times, 1)[times % 10 == 0],
               xticklabels=times[times % 10 == 0])

    ax.set_xlabel('Time Windows' if times is None else 'Time (s)')
    ax.set_ylabel('Frequency')
