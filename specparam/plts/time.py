"""Plots for the time model object.

Notes
-----
This file contains plotting functions that take as input a time model object.
"""

from itertools import cycle

from specparam.utils.select import find_first_ind
from specparam.plts.utils import savefig
from specparam.plts.templates import plot_params_over_time
from specparam.plts.settings import PARAM_COLORS
from specparam.modutils.errors import NoModelError
from specparam.modutils.dependencies import safe_import, check_dependency

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_time_model(time, **plot_kwargs):
    """Plot a figure with subplots visualizing the parameters from a SpectralTimeModel object.

    Parameters
    ----------
    time : SpectralTimeModel
        Object containing results from fitting power spectra across time windows.
    **plot_kwargs
        Keyword arguments to apply to the plot.

    Raises
    ------
    NoModelError
        If the model object does not have model fit data available to plot.
    """

    if not time.results.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    axes = plot_kwargs.pop('axes', None)
    if axes is None:
        _, axes = plt.subplots(\
            2 + time.results.bands.n_bands, 1, gridspec_kw={'hspace' : 0.4},
            figsize=plot_kwargs.pop('figsize', [10, 4 + 2 * time.results.bands.n_bands]))
    axes = cycle(axes)

    xlim = [0, time.data.n_time_windows - 1]

    # 01: aperiodic parameters
    plot_params_over_time(None, \
        [time.results.time_results[alabel] for alabel in time.modes.aperiodic.params.labels],
        labels=time.modes.aperiodic.params.labels, add_xlabel=False, xlim=xlim,
        colors=[PARAM_COLORS[alabel] for alabel in time.modes.aperiodic.params.labels],
        title='Aperiodic Parameters', ax=next(axes))

    # 02: periodic parameters
    for blabel in time.results.bands.labels:
        plot_params_over_time(None, \
            [time.results.time_results[blabel + '_' + plabel] \
                for plabel in time.modes.periodic.params.labels],
            labels=[plabel.upper() for plabel in time.modes.periodic.params.labels],
            add_xlabel=False, xlim=xlim,
            colors=[PARAM_COLORS[plabel] for plabel in time.modes.periodic.params.labels],
            title='Periodic Parameters - ' + blabel, ax=next(axes))

    # 03: metrics
    err_ind = find_first_ind(time.results.metrics.labels, 'error')
    gof_ind = find_first_ind(time.results.metrics.labels, 'gof')
    plot_params_over_time(None, \
        [time.results.time_results[time.results.metrics.labels[err_ind]],
         time.results.time_results[time.results.metrics.labels[gof_ind]]],
        labels=[time.results.metrics.flabels[err_ind],
                time.results.metrics.flabels[gof_ind]],
        colors=[PARAM_COLORS[time.results.metrics.categories[err_ind]],
                PARAM_COLORS[time.results.metrics.categories[gof_ind]]],
        xlim=xlim, title='Fit Quality', ax=next(axes))
