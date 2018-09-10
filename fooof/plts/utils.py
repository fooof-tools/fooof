"""Utility functions for plotting in FOOOF.

Notes
-----
These utility functions should be considered private.
    They are not expected to be called directly by the user.
"""

from collections import OrderedDict

from fooof.plts.settings import DEFAULT_FIGSIZE
from fooof.core.modutils import safe_import

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def set_alpha(n_pts):
    """Set an alpha value for plot that is scaled by the number of points to be plotted.

    Parameters
    ----------
    n_pts : int
        Number of points that will be in the plot.

    Returns
    -------
    n_pts : float
        Value for alpha to use for plotting.
    """

    alpha_levels = OrderedDict({0 : 0.50, 100  : 0.40, 500  : 0.25, 1000 : 0.10})

    for ke, va in alpha_levels.items():
        if n_pts > ke:
            alpha = va

    return alpha


def add_shades(ax, shades, centers):
    """Add shaded regions to a specified graph.

    Parameters
    ----------
    ax : xx
        xx
    shades :
        xx
    centers :
        xx
    """

    for shade in shades:

        ax.axvspan(shade[0], shade[1], color='r', alpha=0.2, lw=0)

        if centers:
            center = sum(shade) / 2
            ax.axvspan(center, center, color='g')


def check_ax(ax):
    """

    Parameters
    ----------
    ax : xx
        xx

    Returns
    -------
    ax :
        xx
    """

    if not ax:
        _, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    return ax
