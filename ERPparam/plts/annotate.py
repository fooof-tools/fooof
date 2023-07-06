"""Plots for annotating power spectrum fittings and models."""

import numpy as np

from fooof.core.utils import nearest_ind
from fooof.core.errors import NoModelError
from fooof.core.funcs import gaussian_function
from fooof.core.modutils import safe_import, check_dependency

from fooof.sim.gen import gen_aperiodic
from fooof.analysis.periodic import get_band_peak_fm
from fooof.utils.params import compute_knee_frequency, compute_fwhm

from fooof.plts.spectra import plot_spectra
from fooof.plts.utils import check_ax, savefig
from fooof.plts.settings import PLT_FIGSIZES, PLT_COLORS
from fooof.plts.style import style_spectrum_plot

plt = safe_import('.pyplot', 'matplotlib')
mpatches = safe_import('.patches', 'matplotlib')

###################################################################################################
###################################################################################################

@savefig
@check_dependency(plt, 'matplotlib')
def plot_annotated_peak_search(fm):
    """Plot a series of plots illustrating the peak search from a flattened spectrum.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object, with model fit, data and settings available.
    """

    # Recalculate the initial aperiodic fit and flattened spectrum that
    #   is the same as the one that is used in the peak fitting procedure
    flatspec = fm.power_spectrum - \
        gen_aperiodic(fm.freqs, fm._robust_ap_fit(fm.freqs, fm.power_spectrum))

    # Calculate ylims of the plot that are scaled to the range of the data
    ylims = [min(flatspec) - 0.1 * np.abs(min(flatspec)), max(flatspec) + 0.1 * max(flatspec)]

    # Sort parameters by peak height
    gaussian_params = fm.gaussian_params_[fm.gaussian_params_[:, 1].argsort()][::-1]

    # Loop through the iterative search for each peak
    for ind in range(fm.n_peaks_ + 1):

        # This forces the creation of a new plotting axes per iteration
        ax = check_ax(None, PLT_FIGSIZES['spectral'])

        plot_spectra(fm.freqs, flatspec, ax=ax, linewidth=2.5,
                     label='Flattened Spectrum', color=PLT_COLORS['data'])
        plot_spectra(fm.freqs, [fm.peak_threshold * np.std(flatspec)]*len(fm.freqs), ax=ax,
                     label='Relative Threshold', color='orange', linewidth=2.5, linestyle='dashed')
        plot_spectra(fm.freqs, [fm.min_peak_height]*len(fm.freqs), ax=ax,
                     label='Absolute Threshold', color='red', linewidth=2.5, linestyle='dashed')

        maxi = np.argmax(flatspec)
        ax.plot(fm.freqs[maxi], flatspec[maxi], '.',
                color=PLT_COLORS['periodic'], alpha=0.75, markersize=30)

        ax.set_ylim(ylims)
        ax.set_title('Iteration #' + str(ind+1), fontsize=16)

        if ind < fm.n_peaks_:

            gauss = gaussian_function(fm.freqs, *gaussian_params[ind, :])
            plot_spectra(fm.freqs, gauss, ax=ax, label='Gaussian Fit',
                         color=PLT_COLORS['periodic'], linestyle=':', linewidth=3.0)

            flatspec = flatspec - gauss

        style_spectrum_plot(ax, False, True)


@savefig
@check_dependency(plt, 'matplotlib')
def plot_annotated_model(fm, plt_log=False, annotate_peaks=True,
                         annotate_aperiodic=True, ax=None):
    """Plot a an annotated power spectrum and model, from a FOOOF object.

    Parameters
    ----------
    fm : FOOOF
        FOOOF object, with model fit, data and settings available.
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
    if not fm.has_model:
        raise NoModelError("No model is available to plot, can not proceed.")

    # Settings
    fontsize = 15
    lw1 = 4.0
    lw2 = 3.0
    ms1 = 12

    # Create the baseline figure
    ax = check_ax(ax, PLT_FIGSIZES['spectral'])
    fm.plot(plot_peaks='dot-shade-width', plt_log=plt_log, ax=ax,
            data_kwargs={'lw' : lw1, 'alpha' : 0.6},
            aperiodic_kwargs={'lw' : lw1, 'zorder' : 10},
            model_kwargs={'lw' : lw1, 'alpha' : 0.5},
            peak_kwargs={'dot' : {'color' : PLT_COLORS['periodic'], 'ms' : ms1, 'lw' : lw2},
                         'shade' : {'color' : PLT_COLORS['periodic']},
                         'width' : {'color' : PLT_COLORS['periodic'], 'alpha' : 0.75, 'lw' : lw2}})

    # Get freqs for plotting, and convert to log if needed
    freqs = fm.freqs if not plt_log else np.log10(fm.freqs)

    ## Buffers: for spacing things out on the plot (scaled by plot values)
    x_buff1 = max(freqs) * 0.1
    x_buff2 = max(freqs) * 0.25
    y_buff1 = 0.15 * np.ptp(ax.get_ylim())
    shrink = 0.1

    # There is a bug in annotations for some perpendicular lines, so add small offset
    #   See: https://github.com/matplotlib/matplotlib/issues/12820. Fixed in 3.2.1.
    bug_buff = 0.000001

    if annotate_peaks and fm.n_peaks_:

        # Extract largest peak, to annotate, grabbing gaussian params
        gauss = get_band_peak_fm(fm, fm.freq_range, attribute='gaussian_params')

        peak_ctr, peak_hgt, peak_wid = gauss
        bw_freqs = [peak_ctr - 0.5 * compute_fwhm(peak_wid),
                    peak_ctr + 0.5 * compute_fwhm(peak_wid)]

        if plt_log:
            peak_ctr = np.log10(peak_ctr)
            bw_freqs = np.log10(bw_freqs)

        peak_top = fm.power_spectrum[nearest_ind(freqs, peak_ctr)]

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
        ax.plot([freqs[0], freqs[0]], [ax.get_ylim()[0], fm.fooofed_spectrum_[0]],
                color=PLT_COLORS['aperiodic'], linewidth=lw2, alpha=0.5)
        ax.annotate('Offset',
                    xy=(freqs[0]+bug_buff, fm.power_spectrum[0]-y_buff1),
                    xytext=(freqs[0]-x_buff1, fm.power_spectrum[0]-y_buff1),
                    verticalalignment='center',
                    horizontalalignment='center',
                    arrowprops=dict(facecolor=PLT_COLORS['aperiodic'], shrink=shrink),
                    color=PLT_COLORS['aperiodic'], fontsize=fontsize)

        # Annotate Aperiodic Knee
        if fm.aperiodic_mode == 'knee':

            # Find the knee frequency point to annotate
            knee_freq = compute_knee_frequency(fm.get_params('aperiodic', 'knee'),
                                               fm.get_params('aperiodic', 'exponent'))
            knee_freq = np.log10(knee_freq) if plt_log else knee_freq
            knee_pow = fm.power_spectrum[nearest_ind(freqs, knee_freq)]

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
                    xy=(freqs[mid_ind], fm.power_spectrum[mid_ind]),
                    xytext=(freqs[mid_ind]-x_buff2, fm.power_spectrum[mid_ind]-y_buff1),
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
