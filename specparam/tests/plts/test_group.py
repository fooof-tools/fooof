"""Tests for specparam.plts.group."""

from pytest import raises

from specparam import SpectralGroupModel
from specparam.modutils.errors import NoModelError

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.group import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_group_model(tfg, skip_if_no_mpl):

    plot_group_model(tfg, file_path=TEST_PLOTS_PATH,
                     file_name='test_plot_group_model.png')

    # Test error if no data available to plot
    tfg = SpectralGroupModel()
    with raises(NoModelError):
        tfg.plot()

@plot_test
def test_plot_group_aperiodic(tfg, skip_if_no_mpl):

    plot_group_aperiodic(tfg, file_path=TEST_PLOTS_PATH,
                         file_name='test_plot_group_aperiodic.png')

@plot_test
def test_plot_group_goodness(tfg, skip_if_no_mpl):

    plot_group_goodness(tfg, file_path=TEST_PLOTS_PATH,
                        file_name='test_plot_group_goodness.png')

@plot_test
def test_plot_group_peak_frequencies(tfg, skip_if_no_mpl):

    plot_group_peak_frequencies(tfg, file_path=TEST_PLOTS_PATH,
                                file_name='test_plot_group_peak_frequencies.png')
