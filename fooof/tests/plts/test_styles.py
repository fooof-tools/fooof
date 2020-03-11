"""Tests for fooof.plts.styles."""

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
