"""Power spectrum plotting functions, for FOOOF.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from itertools import repeat

import numpy as np

from fooof.core.modutils import safe_import, check_dependency

from fooof.plts.settings import DEFAULT_FIGSIZE
from fooof.plts.utils import check_ax, add_shades
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
        X-axis data, frequency values.
    power_spectrum : 1d array
        Y-axis data, power values for spectrum to plot.
    log_freqs : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    log_powers : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    # Create plot axes, if not provided
    if not ax:
        _, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    # Set plot data & labels, logging if requested
    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectrum) if log_powers else power_spectrum

    # Set default plot settings, that only apply if not over-written in kwargs
    if 'linewidth' not in kwargs:
        kwargs['linewidth'] = 2.0

    # Create the plot & style
    ax.plot(plt_freqs, plt_powers, **kwargs)
    check_n_style(plot_style, ax, log_freqs, log_powers)


@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False, labels=None,
                 ax=None, plot_style=style_spectrum_plot, **kwargs):
    """Plot multiple power spectra on the same plot.

    Parameters
    ----------
    freqs : 2d array or 1d array or list of 1d array
        X-axis data, frequency values.
    power_spectra : 2d array or list of 1d array
        Y-axis data, power values for spectra to plot.
    log_freqs : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    log_powers : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    labels " "
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    freqs = repeat(freqs) if isinstance(freqs, np.ndarray) and freqs.ndim == 1 else freqs
    labels = repeat(labels) if not isinstance(labels, list) else labels

    ax = check_ax(ax)
    for freq, power_spectrum, label in zip(freqs, power_spectra, labels):
        plot_spectrum(freq, power_spectrum, log_freqs, log_powers, label=label,
                      plot_style=None, ax=ax, **kwargs)
    check_n_style(plot_style, ax, log_freqs, log_powers)


@check_dependency(plt, 'matplotlib')
def plot_spectrum_shading(freqs, power_spectrum, shades, add_center=False,
                          ax=None, plot_style=style_spectrum_plot, **kwargs):
    """Plot a power spectrum with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    power_spectrum : 1d array
        Y-axis data, power values for spectrum to plot.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    add_center : boolean, optional, default: False
        Whether to add a line at the center point of the shaded regions.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax)
    plot_spectrum(freqs, power_spectrum, plot_style=None, ax=ax, **kwargs)
    add_shades(ax, shades, add_center, kwargs.get('log_freqs', False))
    check_n_style(plot_style, ax, kwargs.get('log_freqs', False), kwargs.get('log_powers', False))


@check_dependency(plt, 'matplotlib')
def plot_spectra_shading(freqs, power_spectra, shades, add_center=False,
                         ax=None, plot_style=style_spectrum_plot, **kwargs):
    """Plot a group of power spectra with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 2d array or 1d array or list of 1d array
        X-axis data, frequency values.
    power_spectra : 2d array or list of 1d array
        Y-axis data, power values for spectra to plot.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    add_center : boolean, optional, default: False
        Whether to add a line at the center point of the shaded regions.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **kwargs
        Keyword arguments to be passed to plot_spectra or the plot call.

    Notes
    -----
    Parameters for `plot_spectra` can also be passed into this function as **kwargs.
    This includes `log_freqs`, `log_powers` & `labels`. See `plot_spectra for usage details.
    """

    ax = check_ax(ax)
    plot_spectra(freqs, power_spectra, ax=ax, plot_style=None, **kwargs)
    add_shades(ax, shades, add_center, kwargs.get('log_freqs', False))
    check_n_style(plot_style, ax, kwargs.get('log_freqs', False), kwargs.get('log_powers', False))
