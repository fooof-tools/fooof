"""Plots for FOOOFGroup object.

Notes
-----
This file contains plotting functions that take as input a FOOOFGroup() object.
"""

from fooof.core.io import fname, fpath
from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.templates import plot_scatter_1, plot_scatter_2, plot_hist

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_fg(fg, save_fig=False, file_name='FOOOF_group_fit', file_path=None):
    """Plots a figure with subplots covering the group results from a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup() object
        FOOOFGroup object, containing results from fitting a group of power spectra.
    save_fig : boolean, optional, default: False
        Whether to save out a copy of the plot.
    file_name : str, optional
        Name to give the saved out file.
    file_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    """

    if not fg.group_results:
        raise RuntimeError('No data available to plot - can not proceed.')

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, wspace=0.35, hspace=0.25, height_ratios=[1, 1.2])

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
        plt.savefig(fpath(file_path, fname(file_name, 'png')))


@check_dependency(plt, 'matplotlib')
def plot_fg_ap(fg, ax=None):
    """Plot aperiodic fit parameters, in a scatter plot.

    Parameters
    ----------
    fg : FOOOFGroup() object
        Group object from which to plot data.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    if fg.aperiodic_mode == 'knee':
        plot_scatter_2(fg.get_params('aperiodic_params', 1), 'Knee',
                       fg.get_params('aperiodic_params', 2), 'Exponent',
                       'Aperiodic Fit', ax=ax)
    else:
        plot_scatter_1(fg.get_params('aperiodic_params', 1), 'Exponent',
                       'Aperiodic Fit', ax=ax)


@check_dependency(plt, 'matplotlib')
def plot_fg_gf(fg, ax=None):
    """Plot goodness of fit results, in a scatter plot.

    Parameters
    ----------
    fg : FOOOFGroup() object
        Group object from which to plot data.
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
    fg : FOOOFGroup() object
        Group object from which to plot data.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    plot_hist(fg.get_params('peak_params', 0)[:, 0], 'Center Frequency',
              'Peaks - Center Frequencies', x_lims=fg.freq_range, ax=ax)
