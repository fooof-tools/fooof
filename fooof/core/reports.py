"""Generate reports from FOOOF and FOOOF derivative objects."""

from fooof.core.io import fname, fpath
from fooof.core.modutils import safe_import, check_dependency
from fooof.core.strings import gen_settings_str, gen_results_fm_str, gen_results_fg_str
from fooof.plts.fg import plot_fg_ap, plot_fg_gf, plot_fg_peak_cens

plt = safe_import('.pyplot', 'matplotlib')
gridspec = safe_import('.gridspec', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def save_report_fm(fm, file_name, file_path=None, plt_log=False):
    """Generate and save out a as PDF a report for a FOOOF object.

    Parameters
    ----------
    fm : FOOOF() object
        FOOOF object, containing results from fitting a power spectrum.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    plt_log : bool, optional, default: False
        Whether or not to plot the frequency axis in log space.
    """

    font = _report_settings()

    # Set up outline figure, using gridspec
    fig = plt.figure(figsize=(16, 20))
    grid = gridspec.GridSpec(3, 1, height_ratios=[0.45, 1.0, 0.25])

    # First - text results
    ax0 = plt.subplot(grid[0])
    results_str = gen_results_fm_str(fm)
    ax0.text(0.5, 0.7, results_str, font, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set_xticks([])
    ax0.set_yticks([])

    # Second - data plot
    ax1 = plt.subplot(grid[1])
    fm.plot(plt_log=plt_log, ax=ax1)

    # Third - FOOOF settings
    ax2 = plt.subplot(grid[2])
    settings_str = gen_settings_str(fm, False)
    ax2.text(0.5, 0.1, settings_str, font, ha='center', va='center')
    ax2.set_frame_on(False)
    ax2.set_xticks([])
    ax2.set_yticks([])

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, 'pdf')))
    plt.close()


@check_dependency(plt, 'matplotlib')
def save_report_fg(fg, file_name, file_path=None):
    """Generate and save out as a PDF a report for a FOOOFGroup object.

    Parameters
    ----------
    fg : FOOOFGroup() object
        FOOOFGroup object, containing results from fitting a group of power spectra.
    file_name : str
        Name to give the saved out file.
    file_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    """

    font = _report_settings()

    # Initialize figure
    fig = plt.figure(figsize=(16, 20))
    gs = gridspec.GridSpec(3, 2, wspace=0.35, hspace=0.25, height_ratios=[0.8, 1.0, 1.0])

    # First / top: text results
    ax0 = plt.subplot(gs[0, :])
    results_str = gen_results_fg_str(fg)
    ax0.text(0.5, 0.7, results_str, font, ha='center', va='center')
    ax0.set_frame_on(False)
    ax0.set_xticks([])
    ax0.set_yticks([])

    # Aperiodic parameters plot
    ax1 = plt.subplot(gs[1, 0])
    plot_fg_ap(fg, ax1)

    # Goodness of fit plot
    ax2 = plt.subplot(gs[1, 1])
    plot_fg_gf(fg, ax2)

    # Peak center frequencies plot
    ax3 = plt.subplot(gs[2, :])
    plot_fg_peak_cens(fg, ax3)

    # Save out the report
    plt.savefig(fpath(file_path, fname(file_name, 'pdf')))
    plt.close()


def _report_settings():
    """Return settings to be used for all reports."""

    # Set the font description for saving out text with matplotlib
    font = {'family': 'monospace',
            'weight': 'normal',
            'size': 16}

    return font
