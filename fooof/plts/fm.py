"""Plots for the FOOOF object.

Notes
-----
This file contains plotting functions that take as input a FOOOF object.
"""

import numpy as np

from fooof.core.utils import nearest_ind
from fooof.core.modutils import safe_import, check_dependency
from fooof.sim.gen import gen_periodic
from fooof.utils.data import trim_spectrum
from fooof.utils.params import compute_fwhm
from fooof.plts.spectra import plot_spectra
from fooof.plts.settings import PLT_FIGSIZES, PLT_COLORS
from fooof.plts.utils import check_ax, check_plot_kwargs, savefig
from fooof.plts.style import style_spectrum_plot, style_plot

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_fm(fm, plot_peaks=None, plot_aperiodic=True, plt_log=False, add_legend=True,
            save_fig=False, file_name=None, file_path=None, ax=None, data_kwargs=None,
            model_kwargs=None, aperiodic_kwargs=None, peak_kwargs=None, **plot_kwargs):
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
    data_kwargs, model_kwargs, aperiodic_kwargs, peak_kwargs : None or dict, optional
        Keyword arguments to pass into the plot call for each plot element.
    **plot_kwargs
        Keyword arguments to pass into the ``style_plot``.

    Notes
    -----
    Since FOOOF objects store power values in log spacing,
    the y-axis (power) is plotted in log spacing by default.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Log settings - note that power values in FOOOF objects are already logged
    log_freqs = plt_log
    log_powers = False

    # Plot the data, if available
    if fm.has_data:
        data_defaults = {'color' : PLT_COLORS['data'], 'linewidth' : 2.0,
                         'label' : 'Original Spectrum' if add_legend else None}
        data_kwargs = check_plot_kwargs(data_kwargs, data_defaults)
        plot_spectra(fm.freqs, fm.power_spectrum, log_freqs, log_powers, ax=ax, **data_kwargs)

    # Add the full model fit, and components (if requested)
    if fm.has_model:
        model_defaults = {'color' : PLT_COLORS['model'], 'linewidth' : 3.0, 'alpha' : 0.5,
                          'label' : 'Full Model Fit' if add_legend else None}
        model_kwargs = check_plot_kwargs(model_kwargs, model_defaults)
        plot_spectra(fm.freqs, fm.fooofed_spectrum_, log_freqs, log_powers, ax=ax, **model_kwargs)

        # Plot the aperiodic component of the model fit
        if plot_aperiodic:
            aperiodic_defaults = {'color' : PLT_COLORS['aperiodic'], 'linewidth' : 3.0,
                                  'alpha' : 0.5, 'linestyle' : 'dashed',
                                  'label' : 'Aperiodic Fit' if add_legend else None}
            aperiodic_kwargs = check_plot_kwargs(aperiodic_kwargs, aperiodic_defaults)
            plot_spectra(fm.freqs, fm._ap_fit, log_freqs, log_powers, ax=ax, **aperiodic_kwargs)

        # Plot the periodic components of the model fit
        if plot_peaks:
            _add_peaks(fm, plot_peaks, plt_log, ax, peak_kwargs)

    # Apply default style to plot
    style_spectrum_plot(ax, log_freqs, True)


def _add_peaks(fm, approach, plt_log, ax, peak_kwargs):
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
    peak_kwargs : None or dict
        Keyword arguments to pass into the plot call.
        This can be a flat dictionary, with plot keyword arguments,
        or a dictionary of dictionaries, with keys as labels indicating an `approach`,
        and values which contain a dictionary of plot keywords for that approach.

    Notes
    -----
    This is a pass through function, that takes a specification of one
    or multiple add peak approaches to use, and calls the relevant function(s).
    """

    # Input for kwargs could be None, so check if dict and typecast if not
    peak_kwargs = peak_kwargs if isinstance(peak_kwargs, dict) else {}

    # Split up approaches, in case multiple are specified, and apply each
    for cur_approach in approach.split('-'):

        try:

            # This unpacks kwargs, if it's embedded dictionaries for each approach
            plot_kwargs = peak_kwargs.get(cur_approach, peak_kwargs)

            # Pass through to the peak plotting function
            ADD_PEAK_FUNCS[cur_approach](fm, plt_log, ax, **plot_kwargs)

        except KeyError:
            raise ValueError("Plot peak type not understood.")


def _add_peaks_shade(fm, plt_log, ax, **plot_kwargs):
    """Add a shading in of all peaks.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the ``fill_between``.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.25}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in fm.gaussian_params_:

        peak_freqs = np.log10(fm.freqs) if plt_log else fm.freqs
        peak_line = fm._ap_fit + gen_periodic(fm.freqs, peak)

        ax.fill_between(peak_freqs, peak_line, fm._ap_fit, **plot_kwargs)


def _add_peaks_dot(fm, plt_log, ax, **plot_kwargs):
    """Add a short line, from aperiodic to peak, with a dot at the top.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.6, 'lw' : 2.5, 'ms' : 6}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in fm.peak_params_:

        ap_point = np.interp(peak[0], fm.freqs, fm._ap_fit)
        freq_point = np.log10(peak[0]) if plt_log else peak[0]

        # Add the line from the aperiodic fit up the tip of the peak
        ax.plot([freq_point, freq_point], [ap_point, ap_point + peak[1]], **plot_kwargs)

        # Add an extra dot at the tip of the peak
        ax.plot(freq_point, ap_point + peak[1], marker='o', **plot_kwargs)


def _add_peaks_outline(fm, plt_log, ax, **plot_kwargs):
    """Add an outline of each peak.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.7, 'lw' : 1.5}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in fm.gaussian_params_:

        # Define the frequency range around each peak to plot - peak bandwidth +/- 3
        peak_range = [peak[0] - peak[2]*3, peak[0] + peak[2]*3]

        # Generate a peak reconstruction for each peak, and trim to desired range
        peak_line = fm._ap_fit + gen_periodic(fm.freqs, peak)
        peak_freqs, peak_line = trim_spectrum(fm.freqs, peak_line, peak_range)

        # Plot the peak outline
        peak_freqs = np.log10(peak_freqs) if plt_log else peak_freqs
        ax.plot(peak_freqs, peak_line, **plot_kwargs)


def _add_peaks_line(fm, plt_log, ax, **plot_kwargs):
    """Add a long line, from the top of the plot, down through the peak, with an arrow at the top.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.7, 'lw' : 1.4, 'ms' : 10}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    ylims = ax.get_ylim()

    for peak in fm.peak_params_:

        freq_point = np.log10(peak[0]) if plt_log else peak[0]
        ax.plot([freq_point, freq_point], ylims, '-', **plot_kwargs)
        ax.plot(freq_point, ylims[1], 'v', **plot_kwargs)


def _add_peaks_width(fm, plt_log, ax, **plot_kwargs):
    """Add a line across the width of peaks.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.

    Notes
    -----
    This line represents the bandwidth (width or gaussian standard deviation) of
    the peak, though what is literally plotted is the full-width half-max.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.6, 'lw' : 2.5, 'ms' : 6}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in fm.gaussian_params_:

        peak_top = fm.power_spectrum[nearest_ind(fm.freqs, peak[0])]
        bw_freqs = [peak[0] - 0.5 * compute_fwhm(peak[2]),
                    peak[0] + 0.5 * compute_fwhm(peak[2])]

        if plt_log:
            bw_freqs = np.log10(bw_freqs)

        ax.plot(bw_freqs, [peak_top-(0.5*peak[1]), peak_top-(0.5*peak[1])], **plot_kwargs)


# Collect all the possible `add_peak_*` functions together
ADD_PEAK_FUNCS = {
    'shade' : _add_peaks_shade,
    'dot' : _add_peaks_dot,
    'outline' : _add_peaks_outline,
    'line' : _add_peaks_line,
    'width' : _add_peaks_width
}
