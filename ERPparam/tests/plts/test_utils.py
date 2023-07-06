"""Tests for fooof.plts.utils."""

import os

from fooof.core.modutils import safe_import

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

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

    def test_plot(data, ax=None, c=None): ax.plot(data, c=c)

    # Test with no extra inputs
    recursive_plot([[1, 2], [3, 4]], test_plot, check_ax(None))

    # Test with single value input
    recursive_plot([[1, 2], [3, 4]], test_plot, check_ax(None), c='red')

    # Test with list of inputs
    recursive_plot([[1, 2], [3, 4]], test_plot, check_ax(None), c=['red', 'blue'])

    # Test with iterator input
    recursive_plot([[1, 2], [3, 4]], test_plot, check_ax(None), c=iter(['red', 'blue']))

def test_check_plot_kwargs(skip_if_no_mpl):

    # Check empty input
    plot_kwargs = {}
    defaults = {}
    plot_kwargs_out = check_plot_kwargs(plot_kwargs, defaults)
    assert plot_kwargs_out == {}

    # Check None input
    plot_kwargs = None
    defaults = {'alpha' : 0.5}
    plot_kwargs_out = check_plot_kwargs(plot_kwargs, defaults)
    assert plot_kwargs_out == defaults

    # Check it keeps original values, and updates to defaults parameters when missing
    plot_kwargs = {'alpha' : 0.5}
    defaults = {'alpha' : 1, 'linewidth' : 2}
    plot_kwargs = check_plot_kwargs(plot_kwargs, defaults)

    assert len(plot_kwargs) == 2
    assert plot_kwargs['alpha'] == 0.5
    assert plot_kwargs['linewidth'] == 2

def test_savefig():

    @savefig
    def example_plot():
        plt.plot([1, 2], [3, 4])

    # Test defaults to saving given file path & name
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig1.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig1.pdf'))

    # Test works the same when explicitly given `save_fig`
    example_plot(save_fig=True, file_path=TEST_PLOTS_PATH, file_name='test_savefig2.pdf')
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig2.pdf'))

    # Test giving additional save kwargs
    example_plot(file_path=TEST_PLOTS_PATH, file_name='test_savefig3.pdf',
                 save_kwargs={'facecolor' : 'red'})
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig3.pdf'))

    # Test does not save when `save_fig` set to False
    example_plot(save_fig=False, file_path=TEST_PLOTS_PATH, file_name='test_savefig_nope.pdf')
    assert not os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_savefig_nope.pdf'))

def test_save_figure():

    plt.plot([1, 2], [3, 4])
    save_figure(file_name='test_save_figure.pdf', file_path=TEST_PLOTS_PATH)
    assert os.path.exists(os.path.join(TEST_PLOTS_PATH, 'test_save_figure.pdf'))
