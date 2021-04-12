"""Plots for visualizing model error."""

import numpy as np

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.spectra import plot_spectrum
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.style import style_spectrum_plot, style_plot
from fooof.plts.utils import check_ax, savefig

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_spectral_error(freqs, error, shade=None, log_freqs=False, ax=None, **plot_kwargs):
    """Plot frequency by frequency error values.

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
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    plt_freqs = np.log10(freqs) if log_freqs else freqs

    plot_spectrum(plt_freqs, error, ax=ax, linewidth=3)

    if np.any(shade):
        ax.fill_between(plt_freqs, error-shade, error+shade, alpha=0.25)

    ymin, ymax = ax.get_ylim()
    if ymin < 0:
        ax.set_ylim([0, ymax])
    ax.set_xlim(plt_freqs.min(), plt_freqs.max())

    style_spectrum_plot(ax, log_freqs, True)
    ax.set_ylabel('Absolute Error')


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_error_shade(freqs, power_spectra, shade=None, scale=1, log_freqs=False,
                     log_powers=False, ax=None, **plot_kwargs):
    """Plot standard deviation or error as a shaded region around the mean spectrum.

    Parameters
    ----------
    freqs : 1d array
        Frequency values, to be plotted on the x-axis.
    power_spectra : 1d or 2d array
        Power values, to be plotted on the y-axis. ``shade`` must be provided if 1d.
    shade : 1d array, optional, default: None
        Powers to shade above/below the mean spectrum. None defaults to one standard deviation.
    scale : int, optional, default: 1
        Factor to multiply the the standard deviation, or ``shade``, by.
    log_freqs : bool, optional, default: False
        Whether to plot the frequency axis in log spacing.
    log_powers : bool, optional, default: False
        Whether to plot the power axis in log spacing.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.
    **plot_kwargs
        Keyword arguments to be passed to `plot_spectra` or to the plot call.
    """

    if shade is None and power_spectra.ndim != 2:
        raise ValueError('Power spectra must be 2d if shade is not given.')

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Set plot data & labels, logging if requested
    plt_freqs = np.log10(freqs) if log_freqs else freqs
    plt_powers = np.log10(power_spectra) if log_powers else power_spectra

    # Plot mean
    powers_mean = np.mean(plt_powers, axis=0) if plt_powers.ndim == 2 else plt_powers
    ax.plot(plt_freqs, powers_mean)

    # Shade +/- scale * (standard deviation or shade)
    shade = scale * np.std(plt_powers, axis=0) if shade is None else scale * shade
    upper_shade = powers_mean + shade
    lower_shade = powers_mean - shade

    alpha = plot_kwargs.pop('alpha', 0.25)
    ax.fill_between(plt_freqs, lower_shade, upper_shade, alpha=alpha, **plot_kwargs)

    style_spectrum_plot(ax, log_freqs, log_powers)
