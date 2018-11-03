"""Power spectrum plotting functions, for FOOOF.

Notes
-----
This file contains functions for plotting power spectra, that take in data directly.
"""

from fooof.plts.utils import check_ax, add_shades
from fooof.plts.templates import plot_spectrum
from fooof.core.modutils import safe_import, check_dependency

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_spectra(freqs, power_spectra, log_freqs=False, log_powers=False, ax=None, **kwargs):
    """Plot multiple power spectra on the same plot.

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    power_spectra : list of 1d array
        Y-axis data, power spectrum power values for spectra to plot.
    log_freqs : boolean, optional
        Whether or not to take the log of the power axis before plotting. default: False
    log_powers : boolean, optional
        Whether or not to take the log of the power axis before plotting. default: False
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
