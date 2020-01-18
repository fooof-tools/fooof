"""Plots for the FOOOF object.

Notes
-----
This file contains plotting functions that take as input a FOOOF object.
"""

import numpy as np

from fooof.core.io import fname, fpath
from fooof.core.funcs import gaussian_function
from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.utils import check_ax
from fooof.plts.spectra import plot_spectrum
from fooof.plts.settings import FIGSIZE_SPECTRAL
from fooof.plts.style import check_n_style, style_spectrum_plot

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_fm(fm, plt_log=False, save_fig=False, file_name='FOOOF_fit', file_path=None,
            ax=None, plot_style=style_spectrum_plot):
    """Plot the power spectrum and model fit from a FOOOF object.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object, containing a power spectrum and (optionally) results from fitting.
    plt_log : boolean, optional, default: False
        Whether to plot the frequency values in log10 spacing.
    save_fig : bool, optional, default: False
        Whether to save out a copy of the plot.
    file_name : str, optional
        Name to give the saved out file.
    file_path : str, optional
        Path to directory in which to save. If None, saves to current directory.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.

    Notes
    -----
    Since FOOOF objects store power values in log spacing,
    the y-axis (power) is plotted in log spacing, by default.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    # Log settings. Note that power values in FOOOF objects are already logged
    log_freqs = plt_log
    log_powers = False

    # Create the plot, adding data as is available
    if fm.has_data:
        plot_spectrum(fm.freqs, fm.power_spectrum, log_freqs, log_powers,
                      ax=ax, plot_style=None, label='Original Spectrum',
                      color='k', linewidth=2.0)
    if fm.has_model:
        plot_spectrum(fm.freqs, fm.fooofed_spectrum_, log_freqs, log_powers,
                      ax=ax, plot_style=None, label='Full Model Fit',
                      color='r', linewidth=3.0, alpha=0.5)
        plot_spectrum(fm.freqs, fm._ap_fit, log_freqs, log_powers,
                      ax=ax, plot_style=None, label='Aperiodic Fit',
                      color='b', linestyle='dashed', linewidth=3.0, alpha=0.5)

    # Apply style to plot
    check_n_style(plot_style, ax, log_freqs, True)

    # Save out figure, if requested
    if save_fig:
        plt.savefig(fpath(file_path, fname(file_name, 'png')))


@check_dependency(plt, 'matplotlib')
def plot_peak_iter(fm, plot_style=style_spectrum_plot):
    """Plots a series of plots illustrating the peak search from a flattened spectrum.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object, with model fit, data and settings available.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plots.
    """

    flatspec = fm._spectrum_flat
    ylims = [min(flatspec) - 0.1 * np.abs(min(flatspec)), max(flatspec) + 0.1 * max(flatspec)]

    for ind in range(fm.n_peaks_ + 1):

        # This forces the creation of a new plotting axes per iteration
        ax = check_ax(None, FIGSIZE_SPECTRAL)

        plot_spectrum(fm.freqs, flatspec, ax=ax, plot_style=None,
                      label='Flattened Spectrum', linewidth=2.5)
        plot_spectrum(fm.freqs, [fm.peak_threshold * np.std(flatspec)]*len(fm.freqs),
                      ax=ax, plot_style=None, label='Relative Threshold',
                      color='orange', linewidth=2.5, linestyle='dashed')
        plot_spectrum(fm.freqs, [fm.min_peak_height]*len(fm.freqs),
                      ax=ax, plot_style=None, label='Absolute Threshold',
                      color='red', linewidth=2.5, linestyle='dashed')

        maxi = np.argmax(flatspec)
        ax.plot(fm.freqs[maxi], flatspec[maxi], '.', markersize=24)

        ax.set_ylim(ylims)
        ax.set_title('Iteration #' + str(ind+1), fontsize=16)

        if ind < fm.n_peaks_:

            gauss = gaussian_function(fm.freqs, *fm.gaussian_params_[ind, :])
            plot_spectrum(fm.freqs, gauss, ax=ax, plot_style=None,
                          label='Gaussian Fit', linestyle=':', linewidth=2.5)

            flatspec = flatspec - gauss

        check_n_style(plot_style, ax, False, True)
