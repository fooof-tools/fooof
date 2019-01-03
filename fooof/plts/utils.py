"""Utility functions for plotting in FOOOF.

Notes
-----
These utility functions should be considered private.
    They are not expected to be called directly by the user.
"""

from numpy import log10

from fooof.plts.settings import DEFAULT_FIGSIZE, ALPHA_LEVELS
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

    for ke, va in ALPHA_LEVELS.items():
        if n_pts > ke:
            alpha = va

    return alpha


def add_shades(ax, shades, add_center, logged):
    """Add shaded regions to a specified graph.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    add_center : boolean
        Whether to add a line at the center point of the shaded regions.
    logged : boolean
        Whether the shade values should be logged before applying to plot axes.
    """

    # If only only one shade region is specified, this embeds in a list, so that the loop works
    if not isinstance(shades[0], list):
        shades = [shades]

    for shade in shades:

        shade = log10(shade) if logged else shade

        ax.axvspan(shade[0], shade[1], color='r', alpha=0.2, lw=0)

        if add_center:
            center = sum(shade) / 2
            ax.axvspan(center, center, color='g')


def check_ax(ax):
    """Check whether a figure axes object is defined, define if not.

    Parameters
    ----------
    ax : matplotlib.Axes or None
        Axes object to check if is defined.

    Returns
    -------
    ax : matplotlib.Axes
        Figure axes object to use.
    """

    if not ax:
        _, ax = plt.subplots(figsize=DEFAULT_FIGSIZE)

    return ax
