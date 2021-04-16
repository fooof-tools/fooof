"""Tests for fooof.plts.group."""

from py.test import raises

from fooof import FOOOFGroup
from fooof.core.errors import NoModelError

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

from fooof.plts.group import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_group(tfg, skip_if_no_mpl):

    plot_group(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
               file_name='test_plot_group.png')

    # Test error if no data available to plot
    tfg = FOOOFGroup()
    with raises(NoModelError):
        tfg.plot()

@plot_test
def test_plot_group_aperiodic(tfg, skip_if_no_mpl):

    plot_group_aperiodic(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
                  file_name='test_plot_group_aperiodic.png')

@plot_test
def test_plot_group_goodness(tfg, skip_if_no_mpl):

    plot_group_goodness(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
                  file_name='test_plot_group_goodness.png')

@plot_test
def test_plot_group_peak_frequencies(tfg, skip_if_no_mpl):

    plot_group_peak_frequencies(tfg, save_fig=True, file_path=TEST_PLOTS_PATH,
                         file_name='test_plot_group_peak_frequencies.png')
