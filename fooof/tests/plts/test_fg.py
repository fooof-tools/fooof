"""Tests for fooof.plts.fg."""

from pytest import raises

from fooof import FOOOFGroup
from fooof.core.errors import NoModelError

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

from fooof.plts.fg import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fg(tfg, skip_if_no_mpl):

    plot_fg(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
            file_name='test_plot_fg.png')

    # Test error if no data available to plot
    tfg = FOOOFGroup()
    with raises(NoModelError):
        tfg.plot()

@plot_test
def test_plot_fg_ap(tfg, skip_if_no_mpl):

    plot_fg_ap(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
               file_name='test_plot_fg_ap.png')

@plot_test
def test_plot_fg_gf(tfg, skip_if_no_mpl):

    plot_fg_gf(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
               file_name='test_plot_fg_gf.png')

@plot_test
def test_plot_fg_peak_cens(tfg, skip_if_no_mpl):

    plot_fg_peak_cens(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
                      file_name='test_plot_fg_peak_cens.png')
