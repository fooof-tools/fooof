"""Plots for FOOOF object."""

import os
import numpy as np
import matplotlib.pyplot as plt

###################################################################################################
###################################################################################################

def plot_fm(fm, plt_log=False, save_fig=False, save_name='FOOOF_fit', save_path='', ax=None):
    """Plot the original PSD, and full model fit from FOOOF object.

    Parameters
    ----------
    fm : FOOOF() object
        FOOOF object, containing a PSD and (optionally) results from fitting.
    plt_log : boolean, optional
        Whether or not to plot the frequency axis in log space. default: False
    save_fig : boolean, optional
        Whether to save out a copy of the plot. default : False
    save_name : str, optional
        Name to give the saved out file.
    save_path : str, optional
        Path to directory in which to save. If not provided, saves to current directory.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    if not np.all(fm.freqs):
        raise ValueError('No data available to plot - can not proceed.')

    # Set frequency vector, logged if requested
    plt_freqs = np.log10(fm.freqs) if plt_log else fm.freqs

    # Create plot axes, if not provided
    if not ax:
        fig, ax = plt.subplots(figsize=(12, 10))

    # Create the plot
    if np.all(fm.psd):
        ax.plot(plt_freqs, fm.psd, 'k', linewidth=1.0, label='Original PSD')
    if np.all(fm.psd_fit_):
        ax.plot(plt_freqs, fm.psd_fit_, 'r', linewidth=3.0,
                alpha=0.5, label='Full model fit')
        ax.plot(plt_freqs, fm._background_fit, '--b', linewidth=3.0,
                alpha=0.5, label='Background fit')

    ax.set_xlabel('Frequency', fontsize=20)
    ax.set_ylabel('Power', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=16)

    ax.legend(prop={'size': 16})
    ax.grid()

    # Save out figure, if requested
    if save_fig:
        plt.savefig(os.path.join(save_path, save_name + '.png'))
