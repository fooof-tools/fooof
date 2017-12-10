"""Plots for FOOOF object."""

import numpy as np
import matplotlib.pyplot as plt

###################################################################################################
###################################################################################################

def plot_fm(fm, plt_log, save_fig, save_name, save_path, ax):
    """   """

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
