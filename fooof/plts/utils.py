"""Utility functions for plotting.

Notes
-----
These utility functions should be considered private.
They are not expected to be called directly by the user.
"""

from itertools import repeat

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


def add_shades(ax, shades, colors='r', add_center=False, logged=False):
    """Add shaded regions to a plot.

    Parameters
    ----------
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    shades : list of [float, float] or list of list of [float, float]
        Shaded region(s) to add to plot, defined as [lower_bound, upper_bound].
    colors : str or list of string
        Color(s) to plot shades.
    add_center : boolean, default: False
        Whether to add a line at the center point of the shaded regions.
    logged : boolean, default: False
        Whether the shade values should be logged before applying to plot axes.
    """

    # If only only one shade region is specified, this embeds in a list, so that the loop works
    if not isinstance(shades[0], list):
        shades = [shades]

    colors = repeat(colors) if not isinstance(colors, list) else colors

    for shade, color in zip(shades, colors):

        shade = log10(shade) if logged else shade

        ax.axvspan(shade[0], shade[1], color=color, alpha=0.2, lw=0)

        if add_center:
            center = sum(shade) / 2
            ax.axvspan(center, center, color='k', alpha=0.6)


def recursive_plot(data, plot_function, ax, **kwargs):
    """A utility to recursively plot sets of data onto a specified plot.

    Parameters
    ----------
    data : list
        List of datasets to iteratively add to the plot.
    plot_function : callable
        Plot function to call to plot the data.
    ax : matplotlib.Axes
        Figure axes upon which to plot.
    **kwargs
        Keyword arguments to pass into the plot function.
        Should be either a list of values corresponding to length of data, or None.

    Notes
    -----
    The `plot_function` argument must accept the `ax` parameter to specify a plot axis.
    """

    # If there is a list, loop across arrays of data
    if isinstance(data, list):

        # Repeat is used call is to work with None inputs
        # Otherwise, expect a list of values, for each element in data, and so make an iterator
        kwargs = {key : repeat(val) if not isinstance(val, list)
                  else iter(val) for key, val in kwargs.items()}

        # Pass each array of data recursively into plot function
        # Each element of data is added to the same plot axis, with any
        for cur_data in data:

            cur_kwargs = {key: next(val) for key, val in kwargs.items()}
            plot_function(cur_data, ax=ax, **cur_kwargs)
