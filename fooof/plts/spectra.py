"""Power spectrum plotting functions.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from inspect import isfunction
from itertools import repeat, cycle

import numpy as np
from scipy.stats import sem

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.style import style_spectrum_plot, style_plot
from fooof.plts.utils import check_ax, add_shades, savefig, check_plot_kwargs

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False,
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
    colors : list of str, optional, default: None
        Line colors of the spectra.
    labels : list of str, optional, default: None
        Legend labels for the spectra.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Create the plot
    plot_kwargs = check_plot_kwargs(plot_kwargs, {'linewidth' : 2.0})

    # Make inputs iterable if need to be passed multiple times to plot each spectrum
    plt_powers = np.reshape(power_spectra, (1, -1)) if np.ndim(power_spectra) == 1 else \
        power_spectra
    plt_freqs = repeat(freqs) if isinstance(freqs, np.ndarray) and freqs.ndim == 1 else freqs

    # Set labels
    labels = plot_kwargs.pop('label') if 'label' in plot_kwargs.keys() and labels is None else labels
    labels = repeat(labels) if not isinstance(labels, list) else cycle(labels)
    colors = repeat(colors) if not isinstance(colors, list) else cycle(colors)

    # Plot
    for freqs, powers, color, label in zip(plt_freqs, plt_powers, colors, labels):

        # Set plot data, logging if requested, and collect color, if absent
        freqs = np.log10(freqs) if log_freqs else freqs
        powers = np.log10(powers) if log_powers else powers
        if color:
            plot_kwargs['color'] = color

        ax.plot(freqs, powers, label=label, **plot_kwargs)

    style_spectrum_plot(ax, log_freqs, log_powers)


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
        Keyword arguments to pass into :func:`~.plot_spectra`.

    Notes
    -----
    Parameters for `plot_spectra` can also be passed into this function as keyword arguments.

    This includes `log_freqs`, `log_powers` & `labels`. See `plot_spectra` for usage details.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    plot_spectra(freqs, power_spectra, ax=ax, **plot_kwargs)

    add_shades(ax, shades, shade_colors, add_center, plot_kwargs.get('log_freqs', False))

    style_spectrum_plot(ax, plot_kwargs.get('log_freqs', False),
                        plot_kwargs.get('log_powers', False))


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectra_yshade(freqs, power_spectra, shade='std', average='mean', scale=1,
                        log_freqs=False, log_powers=False, color=None, label=None,
                        ax=None, **plot_kwargs):
    """Plot standard deviation or error as a shaded region around the mean spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 1d or 2d array
        Power values, to be plotted on the y-axis. ``shade`` must be provided if 1d.
    shade : 'std', 'sem', 1d array or callable, optional, default: 'std'
        Approach for shading above/below the mean spectrum.
    average : 'mean', 'median' or callable, optional, default: 'mean'
        Averaging approach for the average spectrum to plot. Only used if power_spectra is 2d.
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
        Keyword arguments to be passed to `plot_spectra` or to the plot call.
    """

    if (isinstance(shade, str) or isfunction(shade)) and power_spectra.ndim != 2:
        raise ValueError('Power spectra must be 2d if shade is not given.')

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Set plot data & labels, logging if requested
    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectra) if log_powers else power_spectra

    # Organize mean spectrum to plot
    avg_funcs = {'mean' : np.mean, 'median' : np.median}

    if isinstance(average, str) and plt_powers.ndim == 2:
        avg_powers = avg_funcs[average](plt_powers, axis=0)
    elif isfunction(average) and plt_powers.ndim == 2:
        avg_powers = average(plt_powers)
    else:
        avg_powers = plt_powers

    # Plot average power spectrum
    ax.plot(plt_freqs, avg_powers, linewidth=2.0, color=color, label=label)

    # Organize shading to plot
    shade_funcs = {'std' : np.std, 'sem' : sem}

    if isinstance(shade, str):
        shade_vals = scale * shade_funcs[shade](plt_powers, axis=0)
    elif isfunction(shade):
        shade_vals = scale * shade(plt_powers)
    else:
        shade_vals = scale * shade

    upper_shade = avg_powers + shade_vals
    lower_shade = avg_powers - shade_vals

    # Plot +/- yshading around spectrum
    alpha = plot_kwargs.pop('alpha', 0.25)
    ax.fill_between(plt_freqs, lower_shade, upper_shade,
                    alpha=alpha, color=color, **plot_kwargs)

    style_spectrum_plot(ax, log_freqs, log_powers)
