"""Generate reports from FOOOF objects."""

from fooof.core.io import fname, fpath
from fooof.core.modutils import safe_import, check_dependency
from fooof.core.strings import gen_settings_str, gen_results_fm_str, gen_results_fg_str
from fooof.plts.fg import plot_fg_ap, plot_fg_gf, plot_fg_peak_cens

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

## Settings & Globals
REPORT_FIGSIZE = (16, 20)
REPORT_FONT = {'family': 'monospace',
               'weight': 'normal',
               'size': 16}

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def save_report_fm(fm, file_name, file_path=None, plt_log=False):
    """Generate and save out a PDF report for a power spectrum model fit.

    Parameters
    ----------
    fm : FOOOF
        Object with results from fitting a power spectrum.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    plt_log : bool, optional, default: False
        Whether or not to plot the frequency axis in log space.
    """

    # Set up outline figure, using gridspec
    _ = plt.figure(figsize=REPORT_FIGSIZE)
    grid = gridspec.GridSpec(3, 1, height_ratios=[0.45, 1.0, 0.25])

    # First - text results
    ax0 = plt.subplot(grid[0])
    results_str = gen_results_fm_str(fm)
    ax0.text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set_xticks([])
    ax0.set_yticks([])

    # Second - data plot
    ax1 = plt.subplot(grid[1])
    fm.plot(plt_log=plt_log, ax=ax1)

    # Third - FOOOF settings
    ax2 = plt.subplot(grid[2])
    settings_str = gen_settings_str(fm, False)
    ax2.text(0.5, 0.1, settings_str, REPORT_FONT, ha='center', va='center')
    ax2.set_frame_on(False)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, 'pdf')))
    plt.close()


@check_dependency(plt, 'matplotlib')
def save_report_fg(fg, file_name, file_path=None):
    """Generate and save out a PDF report for a group of power spectrum models.

    Parameters
    ----------
    fg : FOOOFGroup
        Object with results from fitting a group of power spectra.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    """

    # Initialize figure
    _ = plt.figure(figsize=REPORT_FIGSIZE)
    grid = gridspec.GridSpec(3, 2, wspace=0.4, hspace=0.25, height_ratios=[0.8, 1.0, 1.0])

    # First / top: text results
    ax0 = plt.subplot(grid[0, :])
    results_str = gen_results_fg_str(fg)
    ax0.text(0.5, 0.7, results_str, REPORT_FONT, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set_xticks([])
    ax0.set_yticks([])

    # Aperiodic parameters plot
    ax1 = plt.subplot(grid[1, 0])
    plot_fg_ap(fg, ax1)

    # Goodness of fit plot
    ax2 = plt.subplot(grid[1, 1])
    plot_fg_gf(fg, ax2)

    # Peak center frequencies plot
    ax3 = plt.subplot(grid[2, :])
    plot_fg_peak_cens(fg, ax3)

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, 'pdf')))
    plt.close()
