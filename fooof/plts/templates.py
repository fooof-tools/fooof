"""Plot templates for the FOOOF module.

Notes:
- These are template plot structures used in reports and/or other plots.
    - They are not expected to be used / imported separately.
"""

import numpy as np

from fooof.core.modutils import safe_import, check_dependency
from fooof.plts.utils import set_alpha

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

@check_dependency(plt, 'matplotlib')
def plot_scatter_1(data, label, title=None, x_val=0, ax=None):
    """Plot a scatter plot with the given data.

    Parameters
    ----------
    data : 1d array
        Data to plot.
    label : str
        Label for the data, to be set as the y-axis label.
    title : str, optional
        Title for the plot.
    x_val : int, optional, default: 0
        Position along the x-axis to plot set of data.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.

    Notes
    -----
    Data is jittered slightly, for visualization purposes (deviations on x-axis are meaningless).
    """

    if not ax:
        _, ax = plt.subplots()

    # Create x-axis data, with small jitter for visualization purposes
    x_data = np.ones_like(data) * x_val + np.random.normal(0, 0.025, data.shape)

    ax.scatter(x_data, data, s=36, alpha=set_alpha(len(data)))

    if label:
        ax.set_ylabel(label, fontsize=16)

    if title:
        ax.set_title(title, fontsize=20)

    plt.xticks([x_val], [label])
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=10)

    ax.set_xlim([-0.5, 0.5])


@check_dependency(plt, 'matplotlib')
def plot_scatter_2(data_0, label_0, data_1, label_1, title=None, ax=None):
    """Plot a scatter plot with two y-axes, with the given data.

    Parameters
    ----------
    data_0 : 1d array
        Data to plot on the first axis.
    label_0 : str
        Label for the data on the first axis, to be set as the y-axis label.
    data_1 : 1d array
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

    plot_scatter_1(data_0, label_0, ax=ax)
    plot_scatter_1(data_1, label_1, x_val=1, ax=ax1)

    if title:
        ax.set_title(title, fontsize=20)

    ax.set_xlim([-0.5, 1.5])

    plt.xticks([0, 1], [label_0, label_1])
    ax.tick_params(axis='x', labelsize=16)


@check_dependency(plt, 'matplotlib')
def plot_hist(data, label, title=None, n_bins=25, x_lims=None, ax=None):
    """Plot a histogram with the given data.

    Parameters
    ----------
    data : 1d array
        Data to plot.
    label : str
        Label for the data, to be set as the y-axis label.
    title : str, optional
        Title for the plot.
    n_bins : int, optional, default: 25
        Number of bins to use for the histogram.
    x_lims : list of float, optional
        X-axis limits for the plot.
    ax : matplotlib.Axes, optional
        Figure axes upon which to plot.
    """

    if not ax:
        _, ax = plt.subplots()

    ax.hist(data[~np.isnan(data)], n_bins, alpha=0.8)

    ax.set_xlabel(label, fontsize=16)
    ax.set_ylabel('Count', fontsize=16)

    if x_lims:
        ax.set_xlim(x_lims)

    if title:
        ax.set_title(title, fontsize=20)

    ax.tick_params(axis='both', labelsize=12)
