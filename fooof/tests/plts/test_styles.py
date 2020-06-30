"""Tests for fooof.plts.styles."""

from fooof.tests.tutils import plot_test
from fooof.plts.style import *

###################################################################################################
###################################################################################################

def test_check_n_style(skip_if_no_mpl):

    # Check can pass None and do nothing
    check_n_style(None)
    assert True

    # Check can pass a callable
    def checker(*args):
        return True
    check_n_style(checker)

def test_style_spectrum_plot(skip_if_no_mpl):

    # Create a dummy plot and style it
    from fooof.core.modutils import safe_import
    plt = safe_import('.pyplot', 'matplotlib')
    _, ax = plt.subplots()
    style_spectrum_plot(ax, False, False)

    # Check that axis labels are added - use as proxy that it ran correctly
    assert ax.xaxis.get_label().get_text()
    assert ax.yaxis.get_label().get_text()


def test_apply_axis_style():

    _, ax = plt.subplots()

    title = 'Ploty McPlotface'
    xlim = (1.0, 10.0)
    ylabel = 'Line Value'

    apply_axis_style(ax, title=title, xlim=xlim, ylabel=ylabel)

    assert ax.get_title() == title
    assert ax.get_xlim() == xlim
    assert ax.get_ylabel() == ylabel


def test_apply_plot_style():

    # Check applying style to one line
    _, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])

    lw = 4
    apply_plot_style(ax, lw=lw)

    assert ax.get_lines()[0].get_lw() == lw

    # Check applying style across multiple lines
    _, ax = plt.subplots()
    ax.plot([1, 2], [[3, 4], [5, 6]])

    alphas = [0.5, 0.75]
    apply_plot_style(ax, alpha=alphas)

    for line, alpha in zip(ax.get_lines(), alphas):
        assert line.get_alpha() == alpha

    # Check applying style to a scatter plot
    _, ax = plt.subplots()
    ax.scatter([1, 2], [2, 4])
    apply_plot_style(ax, alpha=0.123)
    assert ax.collections[0]._alpha == 0.123

    # Check applying style to a histogram
    _, ax = plt.subplots()
    ax.hist([1, 2, 3])
    apply_plot_style(ax, alpha=0.123)
    assert ax.patches[0]._alpha == 0.123


def test_apply_custom_style():

    _, ax = plt.subplots()
    ax.set_title('placeholder')

    # Test simple application of custom plot style
    apply_custom_style(ax)
    assert ax.title.get_size() == TITLE_FONTSIZE

    # Test adding input parameters to custom plot style
    new_title_fontsize = 15.0
    apply_custom_style(ax, title_fontsize=new_title_fontsize)
    assert ax.title.get_size() == new_title_fontsize


def test_apply_style():

    _, ax = plt.subplots()

    def my_custom_styler(ax, **kwargs):
        ax.set_title('DATA!')

    # Apply plot style using all defaults
    apply_style(ax)

    # Apply plot style passing in a styler
    apply_style(ax, custom_styler=my_custom_styler)


@plot_test
def test_style_plot():

    @style_plot
    def example_plot():
        plt.plot([1, 2], [3, 4])

    def my_plot_style(ax, **kwargs):
        ax.set_title('Custom!')

    # Test with applying default custom styling
    lw = 5
    title = 'Science.'
    example_plot(title=title, lw=lw)

    # Test with passing in own plot_style function
    example_plot(apply_style=my_plot_style)
