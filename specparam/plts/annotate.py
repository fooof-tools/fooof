"""Plots for annotating power spectrum fittings and models."""

import numpy as np

from specparam.utils.select import nearest_ind
from specparam.data.periodic import get_band_peak, sort_peaks
from specparam.measures.params import compute_knee_frequency, compute_fwhm
from specparam.modutils.errors import NoModelError
from specparam.modutils.dependencies import safe_import, check_dependency
from specparam.plts.spectra import plot_spectra
from specparam.plts.utils import check_ax, savefig
from specparam.plts.settings import PLT_FIGSIZES, PLT_COLORS
from specparam.plts.style import style_spectrum_plot

plt = safe_import('.pyplot', 'matplotlib')
mpatches = safe_import('.patches', 'matplotlib')

###################################################################################################
###################################################################################################

def _recompute_flatspec(model, remove_peaks=0):
    """Helper function to recompute the initial flattened spectrum from model fitting.

    Parameters
    ----------
    model : SpectralModel
        Model object, with model fit, data and settings available.
    remove_peaks : int, optional, default: 0
        Number of peak iterations to remove from the flattened spectrum.

    Returns
    -------
    flatspec : 1d array
        Flattened spectrum.
    """

    flatspec = model.data.power_spectrum - \
        model.modes.aperiodic.func(model.data.freqs, \
            *model.algorithm._robust_ap_fit(model.data.freqs, model.data.power_spectrum))

    for peak_ind in range(remove_peaks):
        flatspec = _remove_flatspec_peak(model, flatspec, peak_ind)

    return flatspec


def _remove_flatspec_peak(model, flatspec, peak_ind):
    """Helper function to remove peaks from flattened spectrum.

    Parameters
    ----------
    model : SpectralModel
        Model object, with model fit, data and settings available.
    flatspec : 1d array
        Flattened spectrum.
    peak_ind : int
        Index of the peak to remove from the flattened spectrum.

    Returns
    -------
    flatspec : 1d array
        Flattened spectrum, with peak(s) removed.
    """

    peak_fit_params = sort_peaks(model.results.params.periodic.get_params('fit'), 'PW', 'dec')
    flatspec = flatspec - model.modes.periodic.func(model.data.freqs, *peak_fit_params[peak_ind, :])

    return flatspec


@savefig
@check_dependency(plt, 'matplotlib')
def plot_annotated_peak_search(model):
    """Plot a series of plots illustrating the peak search from a flattened spectrum.

    Parameters
    ----------
    model : SpectralModel
        Model object, with model fit, data and settings available.
    """

    # Calculate ylims of the plot that are scaled to the range of the data
    flatspec = _recompute_flatspec(model)
    ylim = [min(flatspec) - 0.1 * np.abs(min(flatspec)),
            max(flatspec) + 0.1 * max(flatspec)]

    # Loop through the iterative search for each peak
    for peak_ind in range(model.results.n_peaks + 1):
        plot_individual_peak_search(model, peak_ind, flatspec, ylim=ylim)
        if peak_ind != model.results.n_peaks:
            flatspec = _remove_flatspec_peak(model, flatspec, peak_ind)


@savefig
@check_dependency(plt, 'matplotlib')
def plot_individual_peak_search(model, iteration, flatspec=None, ax=None, **plt_kwargs):
    """Plot the process of detecting and fitting an individual peak.

    Parameters
    ----------
    model : SpectralModel
        Model object, with model fit, data and settings available.
    iteration : int
        Which peak iteration to plot.
    flatspec : array, optional
        xx
    plt_kwargs
        Keyword arguments for managing the plot.
    """

    if not model.results.has_model:
        raise NoModelError("No model is available to plot, can not proceed.")

    if flatspec is None:
        flatspec = _recompute_flatspec(model, iteration)

    ax = check_ax(ax, PLT_FIGSIZES['spectral'])

    plot_spectra(model.data.freqs, flatspec, linewidth=2.5,
                 label='Flattened Spectrum', color=PLT_COLORS['data'], ax=ax)
    plot_spectra(model.data.freqs,
                 [model.algorithm.settings.peak_threshold * np.std(flatspec)] \
                    * len(model.data.freqs),
                 label='Relative Threshold', color='orange', linewidth=2.5,
                 linestyle='dashed', ax=ax)
    plot_spectra(model.data.freqs,
                 [model.algorithm.settings.min_peak_height] * len(model.data.freqs),
                 label='Absolute Threshold', color='red', linewidth=2.5,
                 linestyle='dashed', ax=ax)

    maxi = np.argmax(flatspec)
    ax.plot(model.data.freqs[maxi], flatspec[maxi], '.',
            color=PLT_COLORS['periodic'], alpha=0.75, markersize=30)

    ax.set_ylim(plt_kwargs.get('ylim', None))
    ax.set_title(plt_kwargs.get('title', 'Iteration #' + str(iteration+1)), fontsize=16)

    if iteration < model.results.n_peaks:

        peak_fit_params = sort_peaks(model.results.params.periodic.get_params('fit'), 'PW', 'dec')
        cpeak = model.modes.periodic.func(model.data.freqs, *peak_fit_params[iteration, :])
        plot_spectra(model.data.freqs, cpeak, ax=ax, label='Gaussian Fit',
                     color=PLT_COLORS['periodic'], linestyle=':', linewidth=3.0)

    if plt_kwargs.get('restyle', True) is not False:
        style_spectrum_plot(ax, False, True)


@savefig
@check_dependency(plt, 'matplotlib')
def plot_annotated_model(model, plt_log=False, annotate_peaks=True,
                         annotate_aperiodic=True, ax=None):
    """Plot a an annotated power spectrum and model, from a model object.

    Parameters
    ----------
    model : SpectralModel
        Model object, with model fit, data and settings available.
    plt_log : boolean, optional, default: False
        Whether to plot the frequency values in log10 spacing.
    annotate_peaks : boolean, optional, default: True
        Whether to annotate the periodic components of the model fit.
    annotate_aperiodic : boolean, optional, default: True
        Whether to annotate the aperiodic components of the model fit.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.

    Raises
    ------
    NoModelError
        If there are no model results available to plot.
    """

    # Check that model is available
    if not model.results.has_model:
        raise NoModelError("No model is available to plot, can not proceed.")

    # Settings
    fontsize = 15
    lw1 = 4.0
    lw2 = 3.0
    ms1 = 12

    # Create the baseline figure
    ax = check_ax(ax, PLT_FIGSIZES['spectral'])
    model.plot(plot_peaks='dot-shade-width', plt_log=plt_log, ax=ax,
               data_kwargs={'lw' : lw1, 'alpha' : 0.6},
               aperiodic_kwargs={'lw' : lw1, 'zorder' : 10},
               model_kwargs={'lw' : lw1, 'alpha' : 0.5},
               peak_kwargs={'dot' : {'color' : PLT_COLORS['periodic'],
                                     'ms' : ms1, 'lw' : lw2},
                            'shade' : {'color' : PLT_COLORS['periodic']},
                            'width' : {'color' : PLT_COLORS['periodic'],
                                       'alpha' : 0.75, 'lw' : lw2}})

    # Get freqs for plotting, and convert to log if needed
    freqs = model.data.freqs if not plt_log else np.log10(model.data.freqs)

    ## Buffers: for spacing things out on the plot (scaled by plot values)
    x_buff1 = max(freqs) * 0.1
    x_buff2 = max(freqs) * 0.25
    y_buff1 = 0.15 * np.ptp(ax.get_ylim())
    shrink = 0.1

    # There is a bug in annotations for some perpendicular lines, so add small offset
    #   See: https://github.com/matplotlib/matplotlib/issues/12820. Fixed in 3.2.1.
    bug_buff = 0.000001

    if annotate_peaks and model.results.n_peaks:

        # Extract largest peak, to annotate, grabbing peak fit params
        gauss = get_band_peak(model, model.data.freq_range, attribute='fit')

        peak_ctr, peak_hgt, peak_wid = gauss
        bw_freqs = [peak_ctr - 0.5 * compute_fwhm(peak_wid),
                    peak_ctr + 0.5 * compute_fwhm(peak_wid)]

        if plt_log:
            peak_ctr = np.log10(peak_ctr)
            bw_freqs = np.log10(bw_freqs)

        peak_top = model.data.power_spectrum[nearest_ind(freqs, peak_ctr)]

        # Annotate Peak CF
        ax.annotate('Center Frequency',
                    xy=(peak_ctr, peak_top),
                    xytext=(peak_ctr, peak_top+np.abs(0.6*peak_hgt)),
                    verticalalignment='center',
                    horizontalalignment='center',
                    arrowprops=dict(facecolor=PLT_COLORS['periodic'], shrink=shrink),
                    color=PLT_COLORS['periodic'], fontsize=fontsize)

        # Annotate Peak PW
        ax.annotate('Power',
                    xy=(peak_ctr, peak_top-0.3*peak_hgt),
                    xytext=(peak_ctr+x_buff1, peak_top-0.3*peak_hgt),
                    verticalalignment='center',
                    arrowprops=dict(facecolor=PLT_COLORS['periodic'], shrink=shrink),
                    color=PLT_COLORS['periodic'], fontsize=fontsize)

        # Annotate Peak BW
        bw_buff = (peak_ctr - bw_freqs[0])/2
        ax.annotate('Bandwidth',
                    xy=(peak_ctr-bw_buff+bug_buff, peak_top-(0.5*peak_hgt)),
                    xytext=(peak_ctr-bw_buff, peak_top-(1.5*peak_hgt)),
                    verticalalignment='center',
                    horizontalalignment='right',
                    arrowprops=dict(facecolor=PLT_COLORS['periodic'], shrink=shrink),
                    color=PLT_COLORS['periodic'], fontsize=fontsize, zorder=20)

    if annotate_aperiodic:

        # Annotate Aperiodic Offset
        #   Add a line to indicate offset, without adjusting plot limits below it
        ax.set_autoscaley_on(False)
        ax.plot([freqs[0], freqs[0]], [ax.get_ylim()[0], model.results.model.modeled_spectrum[0]],
                color=PLT_COLORS['aperiodic'], linewidth=lw2, alpha=0.5)
        ax.annotate('Offset',
                    xy=(freqs[0]+bug_buff, model.data.power_spectrum[0]-y_buff1),
                    xytext=(freqs[0]-x_buff1, model.data.power_spectrum[0]-y_buff1),
                    verticalalignment='center',
                    horizontalalignment='center',
                    arrowprops=dict(facecolor=PLT_COLORS['aperiodic'], shrink=shrink),
                    color=PLT_COLORS['aperiodic'], fontsize=fontsize)

        # Annotate Aperiodic Knee
        if model.modes.aperiodic.name == 'knee':

            # Find the knee frequency point to annotate
            knee_freq = compute_knee_frequency(model.get_params('aperiodic', 'knee'),
                                               model.get_params('aperiodic', 'exponent'))
            knee_freq = np.log10(knee_freq) if plt_log else knee_freq
            knee_pow = model.data.power_spectrum[nearest_ind(freqs, knee_freq)]

            # Add a dot to the plot indicating the knee frequency
            ax.plot(knee_freq, knee_pow, 'o', color=PLT_COLORS['aperiodic'], ms=ms1*1.5, alpha=0.7)

            ax.annotate('Knee',
                        xy=(knee_freq, knee_pow),
                        xytext=(knee_freq-x_buff2, knee_pow-y_buff1),
                        verticalalignment='center',
                        arrowprops=dict(facecolor=PLT_COLORS['aperiodic'], shrink=shrink),
                        color=PLT_COLORS['aperiodic'], fontsize=fontsize)

        # Annotate Aperiodic Exponent
        mid_ind = int(len(freqs)/2)
        ax.annotate('Exponent',
                    xy=(freqs[mid_ind], model.data.power_spectrum[mid_ind]),
                    xytext=(freqs[mid_ind]-x_buff2, model.data.power_spectrum[mid_ind]-y_buff1),
                    verticalalignment='center',
                    arrowprops=dict(facecolor=PLT_COLORS['aperiodic'], shrink=shrink),
                    color=PLT_COLORS['aperiodic'], fontsize=fontsize)

    # Apply style to plot & tune grid styling
    style_spectrum_plot(ax, plt_log, True)
    ax.grid(True, alpha=0.5)

    # Add labels to plot in the legend
    da_patch = mpatches.Patch(color=PLT_COLORS['data'], label='Original Data')
    ap_patch = mpatches.Patch(color=PLT_COLORS['aperiodic'], label='Aperiodic Parameters')
    pe_patch = mpatches.Patch(color=PLT_COLORS['periodic'], label='Peak Parameters')
    mo_patch = mpatches.Patch(color=PLT_COLORS['model'], label='Full Model')

    handles = [da_patch, ap_patch if annotate_aperiodic else None,
               pe_patch if annotate_peaks else None, mo_patch]
    handles = [el for el in handles if el is not None]

    ax.legend(handles=handles, handlelength=1, fontsize='x-large')
