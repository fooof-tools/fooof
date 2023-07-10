"""Plots for the group model object.

Notes
-----
This file contains plotting functions that take as input a time model object.
"""

from itertools import cycle

from specparam.data.utils import get_periodic_labels
from specparam.plts.utils import savefig
from specparam.plts.templates import plot_params_over_time
from specparam.plts.settings import PARAM_COLORS
from specparam.core.errors import NoModelError
from specparam.core.modutils import safe_import, check_dependency

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_time_model(time_model, save_fig=False, file_name=None, file_path=None, **plot_kwargs):
    """Plot a figure with subplots visualizing the parameters from a SpectralTimeModel object.

    Parameters
    ----------
    time_model : SpectralTimeModel
        Object containing results from fitting power spectra across time windows.
    save_fig : bool, optional, default: False
        Whether to save out a copy of the plot.
    file_name : str, optional
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.

    Raises
    ------
    NoModelError
        If the model object does not have model fit data available to plot.
    """

    if not time_model.has_model:
        raise NoModelError("No model fit results are available, can not proceed.")

    # Check band structure
    pe_labels = get_periodic_labels(time_model.time_results)
    n_bands = len(pe_labels['cf'])

    if plot_kwargs.pop('axes', None) is None:
        _, axes = plt.subplots(2 + n_bands, 1,
                               gridspec_kw={'hspace' : 0.4},
                               figsize=plot_kwargs.pop('figsize', [10, 4 + 2 * n_bands]))
    axes = cycle(axes)

    # 01: aperiodic parameters
    ap_params = [time_model.time_results['offset'],
                 time_model.time_results['exponent']]
    ap_labels = ['Offset', 'Exponent']
    ap_colors = [PARAM_COLORS['offset'],
                 PARAM_COLORS['exponent']]
    if 'knee' in time_model.time_results.keys():
        ap_params.insert(1, time_model.time_results['knee'])
        ap_labels.insert(1, 'Knee')
        ap_colors.insert(1, PARAM_COLORS['knee'])

    plot_params_over_time(ap_params, labels=ap_labels, add_xlabel=False,
                          colors=ap_colors, title='Aperiodic', ax=next(axes))

    # 02: periodic parameters
    for band_ind in range(n_bands):
        plot_params_over_time(\
            [time_model.time_results[pe_labels['cf'][band_ind]],
             time_model.time_results[pe_labels['pw'][band_ind]],
             time_model.time_results[pe_labels['bw'][band_ind]]],
            labels=['CF', 'PW', 'BW'], add_xlabel=False,
            colors=[PARAM_COLORS['cf'], PARAM_COLORS['pw'], PARAM_COLORS['bw']],
            title='Periodic', ax=next(axes))

    # 03: goodness of fit
    plot_params_over_time([time_model.time_results['error'],
                           time_model.time_results['r_squared']],
                          labels=['Error', 'R-squared'],
                          colors=[PARAM_COLORS['error'], PARAM_COLORS['r_squared']],
                          title='Goodness of Fit', ax=next(axes))
