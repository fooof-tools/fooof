"""Utility functions for plotting.

Notes
-----
These utility functions should be considered private.
They are not expected to be called directly by the user.
"""

from itertools import repeat
from collections.abc import Iterator
from functools import wraps

import numpy as np

from fooof.core.io import fname, fpath
from fooof.core.modutils import safe_import
from fooof.core.utils import resolve_aliases
from fooof.plts.settings import PLT_ALPHA_LEVELS, PLT_ALIASES

plt = safe_import('.pyplot', 'matplotlib')

###################################################################################################
###################################################################################################

def check_ax(ax, figsize=None):
    """Check whether a figure axes object is defined, and define if not.

    Parameters
    ----------
    ax : matplotlib.Axes or None
        Object to check if is already an axes object.
    figsize : tuple of float, optional
        Size to create the figure, if not already created.

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

    for key, val in PLT_ALPHA_LEVELS.items():
        if n_points > key:
            alpha = val

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

    # If only one shade region is specified, this embeds in a list, so that the loop works
    if not isinstance(shades[0], list):
        shades = [shades]

    colors = repeat(colors) if not isinstance(colors, list) else colors

    for shade, color in zip(shades, colors):

        shade = np.log10(shade) if logged else shade

        ax.axvspan(shade[0], shade[1], color=color, alpha=0.2, lw=0)

        if add_center:
            center = sum(shade) / 2
            ax.axvspan(center, center, color='k', alpha=0.6)


def recursive_plot(data, plot_function, ax, **kwargs):
    """A utility to recursively plot sets of data.

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
        Inputs can be organized as:

        - a list of values corresponding to length of data, one for each plot call
        - a single value, such as an int, str or None, to be applied to all plot calls

    Notes
    -----
    The `plot_function` argument must accept the `ax` parameter to specify a plot axis.
    """

    # Check and update all inputs to be iterators
    for key, val in kwargs.items():

        # If an input is already an iterator, we can leave as is
        if isinstance(val, Iterator):
            kwargs[key] = val

        # If an input is a list, assume one element per call, and make iterator to do so
        elif isinstance(val, list):
            kwargs[key] = iter(val)

        # Otherwise, assume is a single value to pass to all plot calls, and make repeat to do so
        else:
            kwargs[key] = repeat(val)

    # Pass each array of data recursively into plot function
    #   Each element of data is added to the same plot axis
    for cur_data in data:

        cur_kwargs = {key: next(val) for key, val in kwargs.items()}
        plot_function(cur_data, ax=ax, **cur_kwargs)


def check_plot_kwargs(plot_kwargs, defaults):
    """Check plot keyword arguments, using default values for any missing parameters.

    Parameters
    ----------
    plot_kwargs : dict or None
        Keyword arguments for a plot call.
    defaults : dict
        Any arguments, and their default values, to check and update in 'plot_kwargs'.

    Returns
    -------
    plot_kwargs : dict
        Keyword arguments for a plot call.

    Notes
    -----
    If the input for `plot_kwargs` is None, then `defaults` is returned as `plot_kwargs`.
    """

    if not plot_kwargs:
        return defaults

    for key, value in resolve_aliases(defaults, PLT_ALIASES).items():
        if key not in resolve_aliases(plot_kwargs, PLT_ALIASES):
            plot_kwargs[key] = value

    return plot_kwargs


def savefig(func):
    """Decorator function to save out figures."""

    @wraps(func)
    def decorated(*args, **kwargs):

        # Grab file name and path arguments, if they are in kwargs
        file_name = kwargs.pop('file_name', None)
        file_path = kwargs.pop('file_path', None)

        # Check for an explicit argument for whether to save figure or not
        #   Defaults to saving when file name given (since bool(str)->True; bool(None)->False)
        save_fig = kwargs.pop('save_fig', bool(file_name))

        # Check any collect any other plot keywords
        save_kwargs = kwargs.pop('save_kwargs', {})
        save_kwargs.setdefault('bbox_inches', 'tight')

        # Check and collect whether to close the plot
        close = kwargs.pop('close', None)

        func(*args, **kwargs)

        if save_fig:
            save_figure(file_name, file_path, close, **save_kwargs)

    return decorated


def save_figure(file_name, file_path=None, close=False, **save_kwargs):
    """Save out a figure.

    Parameters
    ----------
    file_name : str
        File name for the figure file to save out.
    file_path : str or Path
        Path for where to save out the figure to.
    close : bool, optional, default: False
        Whether to close the plot after saving.
    save_kwargs
        Additional arguments to pass into the save function.
    """

    full_path = fpath(file_path, fname(file_name, 'png'))
    plt.savefig(full_path, **save_kwargs)

    if close:
        plt.close()
