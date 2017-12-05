"""Plot templates for FOOOF data."""

import numpy as np
import matplotlib.pyplot as plt

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


def plot_hist(dat, label, title, n_bins=20, ax=None):
    """Plot a histogram with the given data.

    Parameters
    ----------
    dat : 1d array
        Data to plot.
    label : str
        Label for the data, to be set as the y-axis label.
    title : str
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

    ax.set_title(title, fontsize=16)
