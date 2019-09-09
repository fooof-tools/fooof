"""Utility functions for plotting.

Notes
-----
These utility functions should be considered private.
They are not expected to be called directly by the user.
"""

from numpy import log10

from fooof.plts.settings import ALPHA_LEVELS
from fooof.core.modutils import safe_import

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def check_ax(ax, figsize=None):
    """Check whether a figure axes object is defined, and define if not.

    Parameters
    ----------
    ax : matplotlib.Axes or None
        Axes object to check if is defined.
    figsize : tuple of float, optional
        Size to create the figure.

    Returns
    -------
    ax : matplotlib.Axes
        Figure axes object to use.
    """

    if not ax:
        _, ax = plt.subplots(figsize=figsize)

    return ax


def set_alpha(n_points):
    """Set an alpha value for plotting that is scaled by the number of points.

    Parameters
    ----------
    n_points : int
        Number of points that will be in the plot.

    Returns
    -------
    alpha : float
        Value for alpha to use for plotting.
    """

    for ke, va in ALPHA_LEVELS.items():
        if n_points > ke:
            alpha = va

    return alpha


def add_shades(ax, shades, add_center, logged):
    """Add shaded regions to a plot.

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
