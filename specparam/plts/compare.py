"""Plots for model comparison."""

from specparam.plts import plot_spectra
from specparam.plts.utils import check_ax
from specparam.plts.settings import PLT_FIGSIZES

###################################################################################################
###################################################################################################

def plot_model_comparison(modelcomp, ax=None, **plot_kwargs):
    """Plot and compare multiple model fits.

    Parameters
    ----------
    modelcomp : ModelComparison
        Model comparison object.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
    """

    import matplotlib as mpl
    cmap = mpl.colormaps['Set1']

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))
    plot_spectra(modelcomp.data.freqs, modelcomp.data.power_spectrum,
                 label='Original Spectrum', lw=3, color='black', ax=ax)
    for ind, model in enumerate(modelcomp.models):
        plot_spectra(modelcomp.data.freqs, model.results.model.modeled_spectrum,
                     color=cmap.colors[ind], alpha=0.65, label=model.modes.label, ax=ax)
