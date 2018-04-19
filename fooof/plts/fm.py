"""Plots for FOOOF object."""

import os
import numpy as np

from fooof.plts.templates import plot_spectrum
from fooof.core.funcs import gaussian_function
from fooof.core.modutils import safe_import, check_dependency

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_fm(fm, plt_log=False, save_fig=False, file_name='FOOOF_fit', file_path='', ax=None):
    """Plot the original power spectrum, and full model fit from FOOOF object.

    Parameters
    ----------
    fm : FOOOF() object
        FOOOF object, containing a power spectrum and (optionally) results from fitting.
    plt_log : boolean, optional
        Whether or not to plot the frequency axis in log space. default: False
    save_fig : boolean, optional
        Whether to save out a copy of the plot. default : False
    file_name : str, optional
        Name to give the saved out file.
    file_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    if not np.all(fm.freqs):
        raise RuntimeError('No data available to plot - can not proceed.')

    if not ax:
        fig, ax = plt.subplots(figsize=(12, 10))

    # Create the plot, adding data as is available
    if np.all(fm.power_spectrum):
        plot_spectrum(fm.freqs, fm.power_spectrum, plt_log, ax,
                      color='k', linewidth=1.25, label='Original Spectrum')
    if np.all(fm.fooofed_spectrum_):
        plot_spectrum(fm.freqs, fm.fooofed_spectrum_, plt_log, ax,
                      color='r', linewidth=3.0, alpha=0.5, label='Full Model Fit')
        plot_spectrum(fm.freqs, fm._bg_fit, plt_log, ax,
                      color='b', linestyle='dashed', linewidth=3.0,
                      alpha=0.5, label='Background Fit')

    # Save out figure, if requested
    if save_fig:
        plt.savefig(os.path.join(file_path, file_name + '.png'))


@check_dependency(plt, 'matplotlib')
def plot_peak_iter(fm):
    """Plots a series of plots illustrating the peak search from a flattened spectrum.

    Parameters
    ----------
    fm : FOOOF() object
        FOOOF object, with model fit and data and settings available.
    """

    flatspec = fm._spectrum_flat
    n_gauss = fm._gaussian_params.shape[0]
    ylims = [min(flatspec) - 0.1 * np.abs(min(flatspec)), max(flatspec) + 0.1 * max(flatspec)]

    for ind in range(n_gauss + 1):

        _, ax = plt.subplots(figsize=(12, 10))

        plot_spectrum(fm.freqs, flatspec, linewidth=2.0, label='Flattened Spectrum', ax=ax)
        plot_spectrum(fm.freqs, [fm.peak_threshold * np.std(flatspec)]*len(fm.freqs),
                      color='orange', linestyle='dashed', label='Relative Threshold', ax=ax)
        plot_spectrum(fm.freqs, [fm.min_peak_amplitude]*len(fm.freqs),
                      color='red', linestyle='dashed', label='Absolute Threshold', ax=ax)

        maxi = np.argmax(flatspec)
        ax.plot(fm.freqs[maxi], flatspec[maxi], '.', markersize=24)

        ax.set_ylim(ylims)
        ax.set_title('Iteration #' + str(ind+1), fontsize=16)

        if ind < n_gauss:

            gauss = gaussian_function(fm.freqs, *fm._gaussian_params[ind, :])
            plot_spectrum(fm.freqs, gauss, label='Gaussian Fit',
                          linestyle=':', linewidth=2.0, ax=ax)

            flatspec = flatspec - gauss
