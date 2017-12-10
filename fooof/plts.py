"""Plot templates for FOOOF data."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

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

def plot_fg(fg, save_fig, save_name, save_path):
    """   """

    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(2, 2, wspace=0.35, hspace=0.25, height_ratios=[1, 1.2])

    # Background parameters plot
    ax0 = plt.subplot(gs[0, 0])
    fg._plot_bg(ax0)

    # Goodness of fit plot
    ax1 = plt.subplot(gs[0, 1])
    fg._plot_gd(ax1)

    # Oscillations plot
    ax2 = plt.subplot(gs[1, :])
    fg._plot_osc_cens(ax2)

    if save_fig:
        plt.savefig(os.path.join(save_path, save_name + '.png'))

###################################################################################################
###################################################################################################

def plot_scatter_1(dat, label, title=None, x_val=0, ax=None):
    """Plot a scatter plot with the given data.

    Parameters
    ----------
    dat : 1d array
        Data to plot.
    label : str
        Label for the data, to be set as the y-axis label.
    title : str, optional
        Title for the plot.
    x_val : int, optional
        Position along the x-axis to plot set of data. default: 0
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.

    Notes
    -----
    Data is jittered slightly, for visualization purposes (deviations on x-axis are meaningless).
    """

    if not ax:
        fig, ax = plt.subplots()

    ax.scatter(np.ones_like(dat) * x_val + np.random.normal(0, 0.025, dat.shape), dat, s=36, alpha=0.5)

    if label:
        ax.set_ylabel(label, fontsize=12)

    if title:
        ax.set_title(title, fontsize=16)

    plt.xticks([x_val], [label], fontsize=12)

    ax.set_xlim([-0.5, 0.5])


def plot_scatter_2(dat_0, label_0, dat_1, label_1, title=None, ax=None):
    """Plot a scatter plot with two y-axes, with the given data.

    Parameters
    ----------
    dat_0 : 1d array
        Data to plot on the first axis.
    label_0 : str
        Label for the data on the first axis, to be set as the y-axis label.
    dat_1 : 1d array
        Data to plot on the second axis.
    label_0 : str
        Label for the data on the second axis, to be set as the y-axis label.
    title : str
        Title for the plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.

    Notes
    -----
    Data is jittered slightly, for visualization purposes (deviations on x-axis are meaningless).
    """

    if not ax:
        fig, ax = plt.subplots()

    ax1 = ax.twinx()

    plot_scatter_1(dat_0, label_0, ax=ax)
    plot_scatter_1(dat_1, label_1, x_val=1, ax=ax1)

    if title:
        ax.set_title(title, fontsize=16)

    ax.set_xlim([-0.5, 1.5])
    plt.xticks([0, 1], [label_0, label_1], fontsize=12)


def plot_hist(dat, label, title=None, n_bins=20, ax=None):
    """Plot a histogram with the given data.

    Parameters
    ----------
    dat : 1d array
        Data to plot.
    label : str
        Label for the data, to be set as the y-axis label.
    title : str, optional
        Title for the plot.
    n_bins : int, optional
        Number of bins to use for the histogram. Default: 20
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    if not ax:
        fig, ax = plt.subplots()

    ax.hist(dat, n_bins, alpha=0.8)

    ax.set_xlabel(label, fontsize=12)
    ax.set_ylabel('Count', fontsize=12)

    if title:
        ax.set_title(title, fontsize=16)
