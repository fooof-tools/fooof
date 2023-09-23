"""Generate reports from model objects."""

from specparam.core.io import fname, fpath
from specparam.core.modutils import safe_import, check_dependency
from specparam.core.strings import (gen_settings_str, gen_model_results_str,
                                    gen_group_results_str)
from specparam.plts.group import (plot_group_aperiodic, plot_group_goodness,
                                  plot_group_peak_frequencies)

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

## Settings & Globals
REPORT_FIGSIZE = (16, 20)
REPORT_FONT = {'family': 'monospace',
               'weight': 'normal',
               'size': 16}
SAVE_FORMAT = 'pdf'

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def save_model_report(model, file_name, file_path=None, plt_log=False,
                      add_settings=True, **plot_kwargs):

    """Generate and save out a PDF report for a power spectrum model fit.

    Parameters
    ----------
    model : SpectralModel
        Object with results from fitting a power spectrum.
    file_name : str
        Name to give the saved out file.
    file_path : Path or str, optional
        Path to directory to save to. If None, saves to current directory.
    plt_log : bool, optional, default: False
        Whether or not to plot the frequency axis in log space.
    add_settings : bool, optional, default: True
        Whether to add a print out of the model settings to the end of the report.
    plot_kwargs : keyword arguments
        Keyword arguments to pass into the plot method.
    """

    # Define grid settings based on what is to be plotted
    n_rows = 3 if add_settings else 2
    height_ratios = [0.5, 1.0, 0.25] if add_settings else [0.45, 1.0]

    # Set up outline figure, using gridspec
    _ = plt.figure(figsize=REPORT_FIGSIZE)
    grid = gridspec.GridSpec(n_rows, 1, hspace=0.25, height_ratios=height_ratios)

    # First - text results
    ax0 = plt.subplot(grid[0])
    results_str = gen_model_results_str(model)
    ax0.text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set(xticks=[], yticks=[])

    # Second - data plot
    ax1 = plt.subplot(grid[1])
    model.plot(plt_log=plt_log, ax=ax1, **plot_kwargs)

    # Third - model settings
    if add_settings:
        ax2 = plt.subplot(grid[2])
        settings_str = gen_settings_str(model, False)
        ax2.text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
        ax2.set_frame_on(False)
        ax2.set(xticks=[], yticks=[])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, SAVE_FORMAT)))
    plt.close()


@check_dependency(plt, 'matplotlib')
def save_group_report(group, file_name, file_path=None, add_settings=True):
    """Generate and save out a PDF report for a group of power spectrum models.

    Parameters
    ----------
    group : SpectralGroupModel
        Object with results from fitting a group of power spectra.
    file_name : str
        Name to give the saved out file.
    file_path : Path or str, optional
        Path to directory to save to. If None, saves to current directory.
    add_settings : bool, optional, default: True
        Whether to add a print out of the model settings to the end of the report.
    """

    # Define grid settings based on what is to be plotted
    n_rows = 4 if add_settings else 3
    height_ratios = [1.0, 1.0, 1.0, 0.5] if add_settings else [0.8, 1.0, 1.0]

    # Initialize figure
    _ = plt.figure(figsize=REPORT_FIGSIZE)
    grid = gridspec.GridSpec(n_rows, 2, wspace=0.35, hspace=0.25, height_ratios=height_ratios)

    # First / top: text results
    ax0 = plt.subplot(grid[0, :])
    results_str = gen_group_results_str(group)
    ax0.text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set(xticks=[], yticks=[])

    # Second - data plots

    # Aperiodic parameters plot
    ax1 = plt.subplot(grid[1, 0])
    plot_group_aperiodic(group, ax1, custom_styler=None)

    # Goodness of fit plot
    ax2 = plt.subplot(grid[1, 1])
    plot_group_goodness(group, ax2, custom_styler=None)

    # Peak center frequencies plot
    ax3 = plt.subplot(grid[2, :])
    plot_group_peak_frequencies(group, ax3, custom_styler=None)

    # Third - Model settings
    if add_settings:
        ax4 = plt.subplot(grid[3, :])
        settings_str = gen_settings_str(group, False)
        ax4.text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
        ax4.set_frame_on(False)
        ax4.set(xticks=[], yticks=[])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, SAVE_FORMAT)))
    plt.close()
