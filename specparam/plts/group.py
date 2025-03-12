"""Plots for the group model object.

Notes
-----
This file contains plotting functions that take as input a group model object.
"""

from specparam.modutils.errors import NoModelError
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.plts.settings import PLT_FIGSIZES
from specparam.plts.templates import plot_scatter_1, plot_scatter_2, plot_hist
from specparam.plts.utils import savefig
from specparam.plts.style import style_plot

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_group_model(group, **plot_kwargs):
    """Plot a figure with subplots visualizing the parameters from a group model object.

    Parameters
    ----------
    group : SpectralGroupModel
        Object containing results from fitting a group of power spectra.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.

    Raises
    ------
    NoModelError
        If the model object does not have model fit data available to plot.
    """

    if not group.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    fig = plt.figure(figsize=plot_kwargs.pop('figsize', PLT_FIGSIZES['group']))
    gs = gridspec.GridSpec(2, 2, wspace=0.35, hspace=0.35, height_ratios=[1, 1.2])

    # Apply scatter kwargs to all subplots
    scatter_kwargs = plot_kwargs
    scatter_kwargs['all_axes'] = True

    # Aperiodic parameters plot
    ax0 = plt.subplot(gs[0, 0])
    plot_group_aperiodic(group, ax0, **scatter_kwargs, custom_styler=None)

    # Goodness of fit plot
    ax1 = plt.subplot(gs[0, 1])
    plot_group_goodness(group, ax1, **scatter_kwargs, custom_styler=None)

    # Center frequencies plot
    ax2 = plt.subplot(gs[1, :])
    plot_group_peak_frequencies(group, ax2, **plot_kwargs, custom_styler=None)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_group_aperiodic(group, ax=None, **plot_kwargs):
    """Plot aperiodic fit parameters, in a scatter plot.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
    """

    if group.aperiodic_mode == 'knee':
        plot_scatter_2(group.get_params('aperiodic_params', 'exponent'), 'Exponent',
                       group.get_params('aperiodic_params', 'knee'), 'Knee',
                       'Aperiodic Fit', ax=ax)
    else:
        plot_scatter_1(group.get_params('aperiodic_params', 'exponent'), 'Exponent',
                       'Aperiodic Fit', ax=ax)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_group_goodness(group, ax=None, **plot_kwargs):
    """Plot goodness of fit results, in a scatter plot.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
    """

    plot_scatter_2(group.get_params('error'), 'Error',
                   group.get_params('r_squared'), 'R^2', 'Goodness of Fit', ax=ax)


@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_group_peak_frequencies(group, ax=None, **plot_kwargs):
    """Plot peak center frequencies, in a histogram.

    Parameters
    ----------
    group : SpectralGroupModel
        Object to plot data from.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.
    """

    plot_hist(group.get_params('peak_params', 0)[:, 0], 'Center Frequency',
              'Peaks - Center Frequencies', x_lims=group.freq_range, ax=ax)
