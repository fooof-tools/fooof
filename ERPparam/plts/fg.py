"""Plots for the FOOOFGroup object.

Notes
-----
This file contains plotting functions that take as input a FOOOFGroup object.
"""

from fooof.core.errors import NoModelError
from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.templates import plot_scatter_1, plot_scatter_2, plot_hist
from fooof.plts.utils import savefig
from fooof.plts.style import style_plot

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_fg(fg, save_fig=False, file_name=None, file_path=None, **plot_kwargs):
    """Plot a figure with subplots visualizing the parameters from a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup
        Object containing results from fitting a group of power spectra.
    save_fig : bool, optional, default: False
        Whether to save out a copy of the plot.
    file_name : str, optional
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.

    Raises
    ------
    NoModelError
        If the FOOOF object does not have model fit data available to plot.
    """

    if not fg.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    fig = plt.figure(figsize=plot_kwargs.pop('figsize', PLT_FIGSIZES['group']))
    gs = gridspec.GridSpec(2, 2, wspace=0.4, hspace=0.25, height_ratios=[1, 1.2])

    # Apply scatter kwargs to all subplots
    scatter_kwargs = plot_kwargs
    scatter_kwargs['all_axes'] = True

    # Aperiodic parameters plot
    ax0 = plt.subplot(gs[0, 0])
    plot_fg_ap(fg, ax0, **scatter_kwargs)

    # Goodness of fit plot
    ax1 = plt.subplot(gs[0, 1])
    plot_fg_gf(fg, ax1, **scatter_kwargs)

    # Center frequencies plot
    ax2 = plt.subplot(gs[1, :])
    plot_fg_peak_cens(fg, ax2, **plot_kwargs)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_fg_ap(fg, ax=None, **plot_kwargs):
    """Plot aperiodic fit parameters, in a scatter plot.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.
    """

    if fg.aperiodic_mode == 'knee':
        plot_scatter_2(fg.get_params('aperiodic_params', 'exponent'), 'Exponent',
                       fg.get_params('aperiodic_params', 'knee'), 'Knee',
                       'Aperiodic Fit', ax=ax)
    else:
        plot_scatter_1(fg.get_params('aperiodic_params', 'exponent'), 'Exponent',
                       'Aperiodic Fit', ax=ax)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_fg_gf(fg, ax=None, **plot_kwargs):
    """Plot goodness of fit results, in a scatter plot.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.
    """

    plot_scatter_2(fg.get_params('error'), 'Error',
                   fg.get_params('r_squared'), 'R^2', 'Goodness of Fit', ax=ax)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_fg_peak_cens(fg, ax=None, **plot_kwargs):
    """Plot peak center frequencies, in a histogram.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.
    """

    plot_hist(fg.get_params('peak_params', 0)[:, 0], 'Center Frequency',
              'Peaks - Center Frequencies', x_lims=fg.freq_range, ax=ax)
