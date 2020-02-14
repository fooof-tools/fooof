"""Power spectrum plotting functions.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from itertools import repeat

import numpy as np

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.utils import check_ax, add_shades
from fooof.plts.settings import FIGSIZE_SPECTRAL
from fooof.plts.style import check_n_style, style_spectrum_plot

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_spectrum(freqs, power_spectrum, log_freqs=False, log_powers=False,
                  ax=None, plot_style=style_spectrum_plot, **kwargs):
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
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    # Set plot data & labels, logging if requested
    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectrum) if log_powers else power_spectrum

    # Set default plot settings, that only apply if not over-written in kwargs
    if 'linewidth' not in kwargs:
        kwargs['linewidth'] = 2.0

    ax.plot(plt_freqs, plt_powers, **kwargs)

    check_n_style(plot_style, ax, log_freqs, log_powers)


@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False, labels=None,
                 ax=None, plot_style=style_spectrum_plot, **kwargs):
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
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    # Make inputs iterable if need to be passed multiple times to plot each spectrum
    freqs = repeat(freqs) if isinstance(freqs, np.ndarray) and freqs.ndim == 1 else freqs
    labels = repeat(labels) if not isinstance(labels, list) else labels

    for freq, power_spectrum, label in zip(freqs, power_spectra, labels):
        plot_spectrum(freq, power_spectrum, log_freqs, log_powers, label=label,
                      plot_style=None, ax=ax, **kwargs)

    check_n_style(plot_style, ax, log_freqs, log_powers)


@check_dependency(plt, 'matplotlib')
def plot_spectrum_shading(freqs, power_spectrum, shades, shade_colors='r', add_center=False,
                          ax=None, plot_style=style_spectrum_plot, **kwargs):
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
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    plot_spectrum(freqs, power_spectrum, plot_style=None, ax=ax, **kwargs)

    add_shades(ax, shades, shade_colors, add_center, kwargs.get('log_freqs', False))

    check_n_style(plot_style, ax, kwargs.get('log_freqs', False), kwargs.get('log_powers', False))


@check_dependency(plt, 'matplotlib')
def plot_spectra_shading(freqs, power_spectra, shades, shade_colors='r', add_center=False,
                         ax=None, plot_style=style_spectrum_plot, **kwargs):
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
    **kwargs
        Keyword arguments to be passed to `plot_spectra` or to the plot call.

    Notes
    -----
    Parameters for `plot_spectra` can also be passed into this function as keyword arguments.

    This includes `log_freqs`, `log_powers` & `labels`. See `plot_spectra` for usage details.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    plot_spectra(freqs, power_spectra, ax=ax, plot_style=None, **kwargs)

    add_shades(ax, shades, shade_colors, add_center, kwargs.get('log_freqs', False))

    check_n_style(plot_style, ax, kwargs.get('log_freqs', False), kwargs.get('log_powers', False))


@check_dependency(plt, 'matplotlib')
def plot_spectrum_error(freqs, error, shade=None, log_freqs=False,
                        ax=None, plot_style=style_spectrum_plot):
    """Plot the frequency by frequency error values.

    Parameters
    ----------
    freqs : 1d array
        Frequency values, to be plotted on the x-axis.
    error : 1d array
        Calculated error values or mean error values across frequencies, to plot on the y-axis.
    shade : 1d array, optional
        Values to shade in around the plotted error.
        This could be, for example, the standard deviation of the errors.
    log_freqs : bool, optional, default: False
        Whether to plot the frequency axis in log spacing.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    plt_freqs = np.log10(freqs) if log_freqs else freqs

    plot_spectrum(plt_freqs, error, linewidth=3, plot_style=None, ax=ax)

    if np.any(shade):
        ax.fill_between(plt_freqs, error-shade, error+shade, alpha=0.25)

    ymin, ymax = ax.get_ylim()
    if ymin < 0:
        ax.set_ylim([0, ymax])
    ax.set_xlim(plt_freqs.min(), plt_freqs.max())

    check_n_style(plot_style, ax, log_freqs, True)
    ax.set_ylabel('Absolute Error')
