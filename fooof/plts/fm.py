"""Plots for the FOOOF object.

Notes
-----
This file contains plotting functions that take as input a FOOOF object.
"""

import numpy as np

from fooof.sim.gen import gen_peaks
from fooof.utils import trim_spectrum
from fooof.sim.gen import gen_aperiodic
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
def plot_fm(fm, plot_peaks=None, plot_aperiodic=True, plt_log=False, add_legend=True,
            save_fig=False, file_name=None, file_path=None,
            ax=None, plot_style=style_spectrum_plot):
    """Plot the power spectrum and model fit results from a FOOOF object.

    Parameters
    ----------
    fm : FOOOF
        Object containing a power spectrum and (optionally) results from fitting.
    plot_peaks : None or {'shade', 'dot', 'outline', 'line'}, optional
        What kind of approach to take to plot peaks. If None, peaks are not specifically plotted.
        Can also be a combination of approaches, separated by '-', for example: 'shade-line'.
    plot_aperiodic : boolean, optional, default: True
        Whether to plot the aperiodic component of the model fit.
    plt_log : boolean, optional, default: False
        Whether to plot the frequency values in log10 spacing.
    add_legend : boolean, optional, default: False
        Whether to add a legend describing the plot components.
    save_fig : bool, optional, default: False
        Whether to save out a copy of the plot.
    file_name : str, optional
        Name to give the saved out file.
    file_path : str, optional
        Path to directory to save to. If None, saves to current directory.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plot.

    Notes
    -----
    Since FOOOF objects store power values in log spacing,
    the y-axis (power) is plotted in log spacing by default.
    """

    ax = check_ax(ax, FIGSIZE_SPECTRAL)

    # Log settings. Note that power values in FOOOF objects are already logged
    log_freqs = plt_log
    log_powers = False

    # Plot the data, if available
    if fm.has_data:
        plot_spectrum(fm.freqs, fm.power_spectrum, log_freqs, log_powers,
                      ax=ax, plot_style=None, color='k', linewidth=2.0,
                      label='Original Spectrum' if add_legend else None)

    # Add the full model fit, and components (if requested)
    if fm.has_model:
        plot_spectrum(fm.freqs, fm.fooofed_spectrum_, log_freqs, log_powers,
                      ax=ax, plot_style=None, color='r', linewidth=3.0, alpha=0.5,
                      label='Full Model Fit' if add_legend else None)

        # Plot the aperiodic component of the model fit
        if plot_aperiodic:
            plot_spectrum(fm.freqs, fm._ap_fit, log_freqs, log_powers,
                          ax=ax, plot_style=None, color='b', linestyle='dashed',
                          linewidth=3.0, alpha=0.5,
                          label='Aperiodic Fit' if add_legend else None)

        # Plot the periodic components of the model fit
        if plot_peaks:
            _add_peaks(fm, plot_peaks, plt_log, ax=ax)

    # Apply style to plot
    check_n_style(plot_style, ax, log_freqs, True)

    # Save out figure, if requested
    if save_fig:
        if not file_name:
            raise ValueError("Input 'file_name' is required to save out the plot.")
        plt.savefig(fpath(file_path, fname(file_name, 'png')))


@check_dependency(plt, 'matplotlib')
def plot_fm_peak_iter(fm, plot_style=style_spectrum_plot):
    """Plot a series of plots illustrating the peak search from a flattened spectrum.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object, with model fit, data and settings available.
    plot_style : callable, optional, default: style_spectrum_plot
        A function to call to apply styling & aesthetics to the plots.
    """

    # Recalculate the initial aperiodic fit and flattened spectrum that
    #   is the same as the one that is used in the peak fitting procedure
    flatspec = fm.power_spectrum - \
        gen_aperiodic(fm.freqs,fm._robust_ap_fit(fm.freqs, fm.power_spectrum))

    # Calculate ylims of the plot that are scaled to the range of the data
    ylims = [min(flatspec) - 0.1 * np.abs(min(flatspec)), max(flatspec) + 0.1 * max(flatspec)]

    # Loop through the iterative search for each peak
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


def _add_peaks(fm, approach, plt_log, ax):
    """Add peaks to a model plot.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    approach : {'shade', 'dot', 'outline', 'outline', 'line'}
        What kind of approach to take to plot peaks.
        Can also be a combination of approaches, separated by '-' (for example 'shade-line').
    plt_log : boolean, optional, default: False
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.

    Notes
    -----
    This is a pass through function, that takes a specification of one
    or multiple add peak approaches to use, and calls the relevant function(s).
    """

    # Split up approaches, in case multiple are specified, and apply each
    for cur_approach in approach.split('-'):
        try:
            ADD_PEAK_FUNCS[cur_approach](fm, plt_log, ax)
        except KeyError:
            raise ValueError("Plot peak type not understood.")


def _add_peaks_shade(fm, plt_log, ax):
    """Add a grey shading in of all peaks.


    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    """

    for peak in fm.get_params('gaussian_params'):

        peak_freqs = np.log10(fm.freqs) if plt_log else fm.freqs
        peak_line = fm._ap_fit + gen_peaks(fm.freqs, peak)

        ax.fill_between(peak_freqs, peak_line, fm._ap_fit, alpha=0.25, color='grey')


def _add_peaks_dot(fm, plt_log, ax):
    """Add a short line, from aperiodic to peak, with a dot at the top.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    """

    for peak in fm.get_params('peak_params'):

        ap_point = np.interp(peak[0], fm.freqs, fm._ap_fit)
        freq_point = np.log10(peak[0]) if plt_log else peak[0]

        # Add the line from the aperiodic fit up the tip of the peak
        ax.plot([freq_point, freq_point], [ap_point, ap_point + peak[1]],
                color='grey', linewidth=2.5, alpha=0.6)

        # Add an extra dot at the tip of the peak
        ax.plot(freq_point, ap_point + peak[1],
                color='grey', marker='o', markersize=6, alpha=0.6)

def _add_peaks_outline(fm, plt_log, ax):
    """Add an outline of each peak, in green.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    """

    for peak in fm.get_params('gaussian_params'):

        # Define the frequency range around each peak to plot - peak bandwidth +/- 3
        peak_range = [peak[0] - peak[2]*3, peak[0] + peak[2]*3]

        # Generate a peak reconstruction for each peak, and trim to desired range
        peak_line = fm._ap_fit + gen_peaks(fm.freqs, peak)
        peak_freqs, peak_line = trim_spectrum(fm.freqs, peak_line, peak_range)

        # Plot the peak outline
        peak_freqs = np.log10(peak_freqs) if plt_log else peak_freqs
        ax.plot(peak_freqs, peak_line, linewidth=1.5, color='green', alpha=0.7)


def _add_peaks_line(fm, plt_log, ax):
    """Add a long line, from the top of the plot, down through the peak, with an arrow at the top.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    """

    ylims = ax.get_ylim()
    for peak in fm.get_params('peak_params'):

        freq_point = np.log10(peak[0]) if plt_log else peak[0]
        ax.plot([freq_point, freq_point], ylims, '-', color='green', alpha=0.6, lw=1.4)
        ax.plot(freq_point, ylims[1], 'v', color='green', alpha=0.75, ms=10)


# Collect all the possible `add_peak_*` functions together
ADD_PEAK_FUNCS = {
    'shade' : _add_peaks_shade,
    'dot' : _add_peaks_dot,
    'outline' : _add_peaks_outline,
    'line' : _add_peaks_line
}
