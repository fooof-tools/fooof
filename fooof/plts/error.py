"""Plots for visualizing model error."""

import numpy as np

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.spectra import plot_spectra
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

    plot_spectra(plt_freqs, error, ax=ax, linewidth=3)

    if np.any(shade):
        ax.fill_between(plt_freqs, error-shade, error+shade, alpha=0.25)

    ymin, ymax = ax.get_ylim()
    if ymin < 0:
        ax.set_ylim([0, ymax])
    ax.set_xlim(plt_freqs.min(), plt_freqs.max())

    style_spectrum_plot(ax, log_freqs, True)
    ax.set_ylabel('Absolute Error')
