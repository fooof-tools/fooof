"""Power spectrum plotting functions.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from itertools import repeat

import numpy as np

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.style import check_n_style, style_spectrum_plot
from fooof.plts.utils import check_ax, add_shades, check_plot_kwargs

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_spectrum(freqs, power_spectrum, log_freqs=False, log_powers=False,
                  ax=None, plot_style=style_spectrum_plot, **plot_kwargs):
    """Plot a power spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectrum : 1d array
        Power values, to be plotted on the y-axis.
    log_freqs : bool, optional, default: False
        Whether to plot the frequency axis in log spacing.
    log_powers : bool, optional, default: False
        Whether to plot the power axis in log spacing.
    ax : matplotlib.Axes, optional
        Figure axis upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Set plot data & labels, logging if requested
    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectrum) if log_powers else power_spectrum

    # Create the plot
    plot_kwargs = check_plot_kwargs(plot_kwargs, {'linewidth' : 2.0})
    ax.plot(plt_freqs, plt_powers, **plot_kwargs)

    check_n_style(plot_style, ax, log_freqs, log_powers)


@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False, labels=None,
                 ax=None, plot_style=style_spectrum_plot, **plot_kwargs):
    """Plot multiple power spectra on the same plot.

    Parameters
    ----------
    freqs : 2d array or 1d array or list of 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 2d array or list of 1d array
        Power values, to be plotted on the y-axis.
    log_freqs : bool, optional, default: False
        Whether to plot the frequency axis in log spacing.
    log_powers : bool, optional, default: False
        Whether to plot the power axis in log spacing.
    labels : list of str, optional
        Legend labels, for each power spectrum.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Make inputs iterable if need to be passed multiple times to plot each spectrum
    freqs = repeat(freqs) if isinstance(freqs, np.ndarray) and freqs.ndim == 1 else freqs
    labels = repeat(labels) if not isinstance(labels, list) else labels

    for freq, power_spectrum, label in zip(freqs, power_spectra, labels):
        plot_spectrum(freq, power_spectrum, log_freqs, log_powers, label=label,
                      plot_style=None, ax=ax, **plot_kwargs)

    check_n_style(plot_style, ax, log_freqs, log_powers)


@check_dependency(plt, 'matplotlib')
def plot_spectrum_shading(freqs, power_spectrum, shades, shade_colors='r', add_center=False,
                          ax=None, plot_style=style_spectrum_plot, **plot_kwargs):
    """Plot a power spectrum with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectrum : 1d array
        Power values, to be plotted on the y-axis.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    shade_colors : str or list of string
        Color(s) to plot shades.
    add_center : bool, optional, default: False
        Whether to add a line at the center point of the shaded regions.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    plot_spectrum(freqs, power_spectrum, plot_style=None, ax=ax, **plot_kwargs)

    add_shades(ax, shades, shade_colors, add_center, plot_kwargs.get('log_freqs', False))

    check_n_style(plot_style, ax,
                  plot_kwargs.get('log_freqs', False),
                  plot_kwargs.get('log_powers', False))


@check_dependency(plt, 'matplotlib')
def plot_spectra_shading(freqs, power_spectra, shades, shade_colors='r', add_center=False,
                         ax=None, plot_style=style_spectrum_plot, **plot_kwargs):
    """Plot a group of power spectra with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 2d array or 1d array or list of 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 2d array or list of 1d array
        Power values, to be plotted on the y-axis.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    shade_colors : str or list of string
        Color(s) to plot shades.
    add_center : bool, optional, default: False
        Whether to add a line at the center point of the shaded regions.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to be passed to `plot_spectra` or to the plot call.

    Notes
    -----
    Parameters for `plot_spectra` can also be passed into this function as keyword arguments.

    This includes `log_freqs`, `log_powers` & `labels`. See `plot_spectra` for usage details.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    plot_spectra(freqs, power_spectra, ax=ax, plot_style=None, **plot_kwargs)

    add_shades(ax, shades, shade_colors, add_center, plot_kwargs.get('log_freqs', False))

    check_n_style(plot_style, ax,
                  plot_kwargs.get('log_freqs', False),
                  plot_kwargs.get('log_powers', False))
