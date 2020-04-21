"""Plots for the FOOOFGroup object.

Notes
-----
This file contains plotting functions that take as input a FOOOFGroup object.
"""

from fooof.core.io import fname, fpath
from fooof.core.errors import NoModelError
from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.settings import PLT_FIGSIZES
from fooof.plts.templates import plot_scatter_1, plot_scatter_2, plot_hist

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_fg(fg, save_fig=False, file_name=None, file_path=None):
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

    fig = plt.figure(figsize=PLT_FIGSIZES['group'])
    gs = gridspec.GridSpec(2, 2, wspace=0.4, hspace=0.25, height_ratios=[1, 1.2])

    # Aperiodic parameters plot
    ax0 = plt.subplot(gs[0, 0])
    plot_fg_ap(fg, ax0)

    # Goodness of fit plot
    ax1 = plt.subplot(gs[0, 1])
    plot_fg_gf(fg, ax1)

    # Center frequencies plot
    ax2 = plt.subplot(gs[1, :])
    plot_fg_peak_cens(fg, ax2)

    if save_fig:
        if not file_name:
            raise ValueError("Input 'file_name' is required to save out the plot.")
        plt.savefig(fpath(file_path, fname(file_name, 'png')))


@check_dependency(plt, 'matplotlib')
def plot_fg_ap(fg, ax=None):
    """Plot aperiodic fit parameters, in a scatter plot.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    if fg.aperiodic_mode == 'knee':
        plot_scatter_2(fg.get_params('aperiodic_params', 'exponent'), 'Knee',
                       fg.get_params('aperiodic_params', 'knee'), 'Exponent',
                       'Aperiodic Fit', ax=ax)
    else:
        plot_scatter_1(fg.get_params('aperiodic_params', 'exponent'), 'Exponent',
                       'Aperiodic Fit', ax=ax)


@check_dependency(plt, 'matplotlib')
def plot_fg_gf(fg, ax=None):
    """Plot goodness of fit results, in a scatter plot.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    plot_scatter_2(fg.get_params('error'), 'Error',
                   fg.get_params('r_squared'), 'R^2', 'Goodness of Fit', ax=ax)


@check_dependency(plt, 'matplotlib')
def plot_fg_peak_cens(fg, ax=None):
    """Plot peak center frequencies, in a histogram.

    Parameters
    ----------
    fg : FOOOFGroup
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    plot_hist(fg.get_params('peak_params', 0)[:, 0], 'Center Frequency',
              'Peaks - Center Frequencies', x_lims=fg.freq_range, ax=ax)
