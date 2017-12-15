"""Plot templates for the FOOOF module."""

import numpy as np
import matplotlib.pyplot as plt

###################################################################################################
###################################################################################################

def plot_psd(freqs, psd, plt_log=False, ax=None, **kwargs):
    """Plot a line plot of a power-spectrum.

    Parameters
    ----------
    freqs : 1d array
        X-axis data, frequency values.
    psd : 1d array
        Y-axis data, PSD power values.
    plt_log : boolean, optional
        Whether or not to plot the frequency axis in log space. default: False
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    **kwargs
        Keyword arguments to be passed to the plot call.
    """

    # Create plot axes, if not provided
    if not ax:
        _, ax = plt.subplots(figsize=(12, 10))

    # Set frequency vector, logged if requested
    plt_freqs = np.log10(freqs) if plt_log else freqs

    # Create the plot
    ax.plot(plt_freqs, psd, **kwargs)

    # Aesthetics and axis labels
    ax.set_xlabel('Frequency', fontsize=20)
    ax.set_ylabel('Power', fontsize=20)
    ax.tick_params(axis='both', which='major', labelsize=16)
    ax.grid(True)

    # If labels were provided, add a legend
    if ax.get_legend_handles_labels()[0]:
        ax.legend(prop={'size': 16})


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
        _, ax = plt.subplots()

    # Create x-axis data, with small jitter for visualization purposes
    x_dat = np.ones_like(dat) * x_val + np.random.normal(0, 0.025, dat.shape)

    ax.scatter(x_dat, dat, s=36, alpha=0.5)

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
        _, ax = plt.subplots()

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
        _, ax = plt.subplots()

    ax.hist(dat, n_bins, alpha=0.8)

    ax.set_xlabel(label, fontsize=12)
    ax.set_ylabel('Count', fontsize=12)

    if title:
        ax.set_title(title, fontsize=16)
