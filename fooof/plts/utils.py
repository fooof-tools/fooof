"""Utility functions for plotting in FOOOF."""

from collections import OrderedDict

###################################################################################################
###################################################################################################

def _set_alpha(n_pts):
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
