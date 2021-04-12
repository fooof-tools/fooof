"""Power spectrum plotting functions.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from itertools import repeat, cycle

import numpy as np

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.style import style_spectrum_plot, style_plot
from fooof.plts.utils import check_ax, add_shades, savefig

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False,
                 colors=None, labels=None, ax=None, **plot_kwargs):
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
    labels : list of str, optional, default: None
        Legend labels for the spectra.
    colors : list of str, optional, default: None
        Line colors of the spectra.
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

        # Set plot data, logging if requested
        freqs = np.log10(freqs) if log_freqs else freqs
        powers = np.log10(powers) if log_powers else powers

        ax.plot(freqs, powers, color=color, label=label, **plot_kwargs)

    style_spectrum_plot(ax, log_freqs, log_powers)

    
@savefig
@check_dependency(plt, 'matplotlib')
def plot_spectra_shading(freqs, power_spectra, shades, shade_colors='r',
                         add_center=False, ax=None, **plot_kwargs):
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
