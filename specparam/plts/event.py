"""Plots for the event model object.

Notes
-----
This file contains plotting functions that take as input an event model object.
"""

from itertools import cycle

from specparam.modutils.errors import NoModelError
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.data.utils import get_periodic_labels, get_band_labels
from specparam.measures.properties import compute_presence
from specparam.plts.utils import savefig
from specparam.plts.templates import plot_param_over_time_yshade
from specparam.plts.settings import PARAM_COLORS

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_event_model(event_model, **plot_kwargs):
    """Plot a figure with subplots visualizing the parameters from a SpectralTimeEventModel object.

    Parameters
    ----------
    event_model : SpectralTimeEventModel
        Object containing results from fitting power spectra across events.
    **plot_kwargs
        Keyword arguments to apply to the plot.

    Raises
    ------
    NoModelError
        If the model object does not have model fit data available to plot.
    """

    if not event_model.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    pe_labels = get_periodic_labels(event_model.event_time_results)
    band_labels = get_band_labels(pe_labels)
    n_bands = len(pe_labels['cf'])

    has_knee = 'knee' in event_model.event_time_results.keys()
    height_ratios = [1] * (3 if has_knee else 2) + [0.25, 1, 1, 1, 1] * n_bands + [0.25] + [1, 1]

    axes = plot_kwargs.pop('axes', None)
    if axes is None:
        _, axes = plt.subplots((4 if has_knee else 3) + (n_bands * 5) + 2, 1,
                               gridspec_kw={'hspace' : 0.1, 'height_ratios' : height_ratios},
                               figsize=plot_kwargs.pop('figsize', [10, 4 + 5 * n_bands]))
    axes = cycle(axes)

    xlim = [0, event_model.n_time_windows - 1]

    # 01: aperiodic params
    alabels = ['offset', 'knee', 'exponent'] if has_knee else ['offset', 'exponent']
    for alabel in alabels:
        plot_param_over_time_yshade(\
            None, event_model.event_time_results[alabel],
            label=alabel, drop_xticks=True, add_xlabel=False, xlim=xlim,
            title='Aperiodic Parameters' if alabel == 'offset' else None,
            color=PARAM_COLORS[alabel], ax=next(axes))
    next(axes).axis('off')

    # 02: periodic params
    for band_ind in range(n_bands):
        for plabel in ['cf', 'pw', 'bw']:
            plot_param_over_time_yshade(None, \
                event_model.event_time_results[pe_labels[plabel][band_ind]],
                label=plabel.upper(), drop_xticks=True, add_xlabel=False, xlim=xlim,
                title='Periodic Parameters - ' + band_labels[band_ind] if plabel == 'cf' else None,
                color=PARAM_COLORS[plabel], ax=next(axes))
        plot_param_over_time_yshade(None, \
            compute_presence(event_model.event_time_results[pe_labels[plabel][band_ind]],
                             output='percent'),
            label='Presence (%)', drop_xticks=True, add_xlabel=False, xlim=xlim,
            color=PARAM_COLORS['presence'], ax=next(axes))
        next(axes).axis('off')

    # 03: goodness of fit
    for glabel in ['error', 'r_squared']:
        plot_param_over_time_yshade(\
            None, event_model.event_time_results[glabel], label=glabel,
            drop_xticks=False if glabel == 'r_squared' else True,
            add_xlabel=True if glabel == 'r_squared' else False,
            title='Goodness of Fit' if glabel == 'error' else None,
            color=PARAM_COLORS[glabel],  xlim=xlim, ax=next(axes))
