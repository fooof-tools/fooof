"""Plots for the event model object.

Notes
-----
This file contains plotting functions that take as input an event model object.
"""

from itertools import cycle

from specparam.modutils.errors import NoModelError
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.measures.properties import compute_presence
from specparam.plts.utils import savefig
from specparam.plts.templates import plot_param_over_time_yshade
from specparam.plts.settings import PARAM_COLORS

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_event_model(event, **plot_kwargs):
    """Plot a figure with subplots visualizing the parameters from a SpectralTimeEventModel object.

    Parameters
    ----------
    event : SpectralTimeEventModel
        Object containing results from fitting power spectra across events.
    **plot_kwargs
        Keyword arguments to apply to the plot.

    Raises
    ------
    NoModelError
        If the model object does not have model fit data available to plot.
    """

    if not event.results.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    height_ratios = [1] * event.modes.aperiodic.n_params + \
        [0.25, 1, 1, 1, 1] * event.results.bands.n_bands + [0.25] + [1, 1]

    axes = plot_kwargs.pop('axes', None)
    if axes is None:
        _, axes = plt.subplots(\
            (event.modes.aperiodic.n_params + 1) + (event.results.bands.n_bands * 5) + 2, 1,
            gridspec_kw={'hspace' : 0.1, 'height_ratios' : height_ratios},
            figsize=plot_kwargs.pop('figsize', [10, 4 + 5 * event.results.bands.n_bands]))
    axes = cycle(axes)

    xlim = [0, event.data.n_time_windows - 1]

    # 01: aperiodic params
    for ind, alabel in enumerate(event.modes.aperiodic.params.labels):
        plot_param_over_time_yshade(\
            None, event.results.event_time_results[alabel],
            label=alabel, drop_xticks=True, add_xlabel=False, xlim=xlim,
            title='Aperiodic Parameters' if ind == 0 else None,
            color=PARAM_COLORS[alabel], ax=next(axes))
    next(axes).axis('off')

    # 02: periodic params
    for bind, blabel in enumerate(event.results.bands.labels):
        for pind, plabel in enumerate(event.modes.periodic.params.labels):
            plot_param_over_time_yshade(None, \
                event.results.event_time_results[blabel + '_' + plabel],
                label=plabel.upper(), drop_xticks=True, add_xlabel=False, xlim=xlim,
                title='Periodic Parameters - ' + \
                    event.results.bands.labels[bind] if pind == 0 else None,
                color=PARAM_COLORS[plabel], ax=next(axes))
        plot_param_over_time_yshade(None, \
            compute_presence(event.results.event_time_results[blabel + '_' + plabel],
                             output='percent'),
            label='Presence (%)', drop_xticks=True, add_xlabel=False, xlim=xlim,
            color=PARAM_COLORS['presence'], ax=next(axes))
        next(axes).axis('off')

    # 03: metrics
    for ind, glabel in enumerate(event.results.metrics.labels):
        plot_param_over_time_yshade(\
            None, event.results.event_time_results[glabel],
            label=event.results.metrics.flabels[ind],
            title='Fit Quality' if ind == 0 else None,
            drop_xticks=ind < len(event.results.metrics),
            add_xlabel=ind == len(event.results.metrics),
            color=PARAM_COLORS[event.results.metrics.categories[ind]],
            xlim=xlim, ax=next(axes))
