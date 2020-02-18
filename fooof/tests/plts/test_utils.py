"""Tests for fooof.plts.utils."""

from fooof.tests.tutils import plot_test

from fooof.core.modutils import safe_import

from fooof.plts.utils import *

mpl = safe_import('matplotlib')

###################################################################################################
###################################################################################################

def test_check_ax(skip_if_no_mpl):

    figsize = [5., 5.]
    ax = check_ax(None, figsize=figsize)

    assert isinstance(ax, mpl.axes.Axes)
    assert figsize == [ax.get_figure().get_figwidth(),
                       ax.get_figure().get_figheight()]

def test_set_alpha(skip_if_no_mpl):

    alpha = set_alpha(100)
    assert isinstance(alpha, float)

@plot_test
def test_add_shades(skip_if_no_mpl):

    add_shades(check_ax(None), [4, 8])

@plot_test
def test_recursive_plot(skip_if_no_mpl):

    def test_plot(data, ax=None): ax.plot(data)
    recursive_plot([[1, 2], [3, 4]], test_plot, check_ax(None))
