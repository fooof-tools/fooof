"""Power spectrum plotting functions, for FOOOF.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

import numpy as np

from fooof.plts.utils import check_ax, add_shades
from fooof.core.modutils import safe_import, check_dependency

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_spectrum(freqs, power_spectrum, log_freqs=False, log_powers=False, ax=None, **kwargs):
    """Plot a power spectrum.

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    power_spectrum : 1d array
        Y-axis data, power_spectrum power values.
    log_freqs : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    log_powers : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    # Create plot axes, if not provided
    if not ax:
        _, ax = plt.subplots(figsize=(12, 10))

    # Check for plot log options in **kwargs, extract if present
    #log_freqs = kwargs.pop('log_freqs', False)
    #log_powers = kwargs.pop('log_powers', False)

    # Set plot data, logging if requested
    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectrum) if log_powers else power_spectrum

    # Create the plot
    ax.plot(plt_freqs, plt_powers, **kwargs)

    # Aesthetics and axis labels
    ax.set_xlabel('Frequency', fontsize=20)
    ax.set_ylabel('Power', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.grid(True)

    # If labels were provided, add a legend
    if ax.get_legend_handles_labels()[0]:
        ax.legend(prop={'size': 16})


@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False, ax=None, **kwargs):
    """Plot multiple power spectra on the same plot.

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    power_spectra : list of 1d array
        Y-axis data, power spectrum power values for spectra to plot.
    log_freqs : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    log_powers : boolean, optional, default: False
        Whether or not to take the log of the power axis before plotting.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    ax = check_ax(ax)
    for power_spectrum in power_spectra:
        plot_spectrum(freqs, power_spectrum, log_freqs, log_powers, ax=ax, **kwargs)


@check_dependency(plt, 'matplotlib')
def plot_spectrum_shading(freqs, power_spectrum, shades, add_center=False, ax=None, **kwargs):
    """Plot a power spectrum with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    power_spectrum : list of 1d array
        Y-axis data, power spectrum power values for spectrum to plot.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    add_center : boolean
        Whether to add a line at the center point of the shaded regions.
    """

    ax = check_ax(ax)
    plot_spectrum(freqs, power_spectrum, ax=ax, **kwargs)
    add_shades(ax, shades, add_center, kwargs.get('log_freqs', False))


@check_dependency(plt, 'matplotlib')
def plot_spectra_shading(freqs, power_spectra, shades, add_center=False, ax=None, **kwargs):
    """Plot a group of power spectra on with a shaded frequency region (or regions).

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    power_spectrum : list of 1d array
        Y-axis data, power spectrum power values for spectrum to plot.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    add_center : boolean
        Whether to add a line at the center point of the shaded regions.
    """

    ax = check_ax(ax)
    plot_spectra(freqs, power_spectra, ax=ax, **kwargs)
    add_shades(ax, shades, add_center, kwargs.get('log_freqs', False))
