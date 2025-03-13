"""Plots for the model object.

Notes
-----
This file contains plotting functions that take as input a model object.
"""

import numpy as np

from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.sim.gen import gen_periodic
from specparam.utils.select import nearest_ind
from specparam.utils.spectral import trim_spectrum
from specparam.measures.params import compute_fwhm
from specparam.plts.spectra import plot_spectra
from specparam.plts.settings import PLT_FIGSIZES, PLT_COLORS
from specparam.plts.utils import check_ax, check_plot_kwargs, savefig
from specparam.plts.style import style_spectrum_plot, style_plot

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@style_plot
@check_dependency(plt, 'matplotlib')
def plot_model(model, plot_peaks=None, plot_aperiodic=True, freqs=None, power_spectrum=None,
               freq_range=None, plt_log=False, add_legend=True, ax=None, data_kwargs=None,
               model_kwargs=None, aperiodic_kwargs=None, peak_kwargs=None, **plot_kwargs):
    """Plot the power spectrum and model fit results from a model object.

    Parameters
    ----------
    model : SpectralModel
        Object containing a power spectrum and (optionally) results from fitting.
    plot_peaks : None or {'shade', 'dot', 'outline', 'line'}, optional
        What kind of approach to take to plot peaks. If None, peaks are not specifically plotted.
        Can also be a combination of approaches, separated by '-', for example: 'shade-line'.
    plot_aperiodic : boolean, optional, default: True
        Whether to plot the aperiodic component of the model fit.
    freqs : 1d array, optional
        Frequency values of the power spectrum to plot, in linear space.
        If provided, this overrides the values in the model object.
    power_spectrum : 1d array, optional
        Power values to plot, in linear space.
        If provided, this overrides the values in the model object.
    freq_range : list of [float, float], optional
        Frequency range to plot, defined in linear space.
    plt_log : boolean, optional, default: False
        Whether to plot the frequency values in log10 spacing.
    add_legend : boolean, optional, default: False
        Whether to add a legend describing the plot components.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    data_kwargs, model_kwargs, aperiodic_kwargs, peak_kwargs : None or dict, optional
        Keyword arguments to pass into the plot call for each plot element.
    **plot_kwargs
        Additional plot related keyword arguments, with styling options managed by ``style_plot``.

    Notes
    -----
    The y-axis (power) is plotted in log spacing by default.
    """

    ax = check_ax(ax, plot_kwargs.pop('figsize', PLT_FIGSIZES['spectral']))

    # Check inputs for what to plot
    custom_spectrum = (np.any(freqs) and np.any(power_spectrum))

    # Log settings - note that power values in model objects are already logged
    log_freqs = plt_log
    log_powers = False

    # Plot the data, if available
    if model.has_data or custom_spectrum:
        data_defaults = {'color' : PLT_COLORS['data'], 'linewidth' : 2.0,
                         'label' : 'Original Spectrum' if add_legend else None}
        data_kwargs = check_plot_kwargs(data_kwargs, data_defaults)
        plot_spectra(freqs if custom_spectrum else model.freqs,
                     power_spectrum if custom_spectrum else model.power_spectrum,
                     log_freqs, log_powers if not custom_spectrum else True,
                     freq_range, ax=ax, **data_kwargs)

    # Add the full model fit, and components (if requested)
    if model.has_model:
        model_defaults = {'color' : PLT_COLORS['model'], 'linewidth' : 3.0, 'alpha' : 0.5,
                          'label' : 'Full Model Fit' if add_legend else None}
        model_kwargs = check_plot_kwargs(model_kwargs, model_defaults)
        plot_spectra(model.freqs, model.modeled_spectrum_,
                     log_freqs, log_powers, ax=ax, **model_kwargs)

        # Plot the aperiodic component of the model fit
        if plot_aperiodic:
            aperiodic_defaults = {'color' : PLT_COLORS['aperiodic'], 'linewidth' : 3.0,
                                  'alpha' : 0.5, 'linestyle' : 'dashed',
                                  'label' : 'Aperiodic Fit' if add_legend else None}
            aperiodic_kwargs = check_plot_kwargs(aperiodic_kwargs, aperiodic_defaults)
            plot_spectra(model.freqs, model._ap_fit,
                         log_freqs, log_powers, ax=ax, **aperiodic_kwargs)

        # Plot the periodic components of the model fit
        if plot_peaks:
            _add_peaks(model, plot_peaks, plt_log, ax, peak_kwargs)

    # Apply default style to plot
    style_spectrum_plot(ax, log_freqs, True)


def _add_peaks(model, approach, plt_log, ax, peak_kwargs):
    """Add peaks to a model plot.

    Parameters
    ----------
    model : SpectralModel
        Model object containing results from fitting.
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
            ADD_PEAK_FUNCS[cur_approach](model, plt_log, ax, **plot_kwargs)

        except KeyError:
            raise ValueError("Plot peak type not understood.")


def _add_peaks_shade(model, plt_log, ax, **plot_kwargs):
    """Add a shading in of all peaks.

    Parameters
    ----------
    model : SpectralModel
        Model object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into ``fill_between``.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.25}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in model.gaussian_params_:

        peak_freqs = np.log10(model.freqs) if plt_log else model.freqs
        peak_line = model._ap_fit + gen_periodic(model.freqs, peak)

        ax.fill_between(peak_freqs, peak_line, model._ap_fit, **plot_kwargs)


def _add_peaks_dot(model, plt_log, ax, **plot_kwargs):
    """Add a short line, from aperiodic to peak, with a dot at the top.

    Parameters
    ----------
    model : SpectralModel
        Model object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.6, 'lw' : 2.5, 'ms' : 6}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in model.peak_params_:

        ap_point = np.interp(peak[0], model.freqs, model._ap_fit)
        freq_point = np.log10(peak[0]) if plt_log else peak[0]

        # Add the line from the aperiodic fit up the tip of the peak
        ax.plot([freq_point, freq_point], [ap_point, ap_point + peak[1]], **plot_kwargs)

        # Add an extra dot at the tip of the peak
        ax.plot(freq_point, ap_point + peak[1], marker='o', **plot_kwargs)


def _add_peaks_outline(model, plt_log, ax, **plot_kwargs):
    """Add an outline of each peak.

    Parameters
    ----------
    model : SpectralModel
        Model object containing results from fitting.
    plt_log : boolean
        Whether to plot the frequency values in log10 spacing.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **plot_kwargs
        Keyword arguments to pass into the plot call.
    """

    defaults = {'color' : PLT_COLORS['periodic'], 'alpha' : 0.7, 'lw' : 1.5}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    for peak in model.gaussian_params_:

        # Define the frequency range around each peak to plot - peak bandwidth +/- 3
        peak_range = [peak[0] - peak[2]*3, peak[0] + peak[2]*3]

        # Generate a peak reconstruction for each peak, and trim to desired range
        peak_line = model._ap_fit + gen_periodic(model.freqs, peak)
        peak_freqs, peak_line = trim_spectrum(model.freqs, peak_line, peak_range)

        # Plot the peak outline
        peak_freqs = np.log10(peak_freqs) if plt_log else peak_freqs
        ax.plot(peak_freqs, peak_line, **plot_kwargs)


def _add_peaks_line(model, plt_log, ax, **plot_kwargs):
    """Add a long line, from the top of the plot, down through the peak, with an arrow at the top.

    Parameters
    ----------
    model : SpectralModel
        Model object containing results from fitting.
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

    for peak in model.peak_params_:

        freq_point = np.log10(peak[0]) if plt_log else peak[0]
        ax.plot([freq_point, freq_point], ylims, '-', **plot_kwargs)
        ax.plot(freq_point, ylims[1], 'v', **plot_kwargs)


def _add_peaks_width(model, plt_log, ax, **plot_kwargs):
    """Add a line across the width of peaks.

    Parameters
    ----------
    model : SpectralModel
        Model object containing results from fitting.
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

    for peak in model.gaussian_params_:

        peak_top = model.power_spectrum[nearest_ind(model.freqs, peak[0])]
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
