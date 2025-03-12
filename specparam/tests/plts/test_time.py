"""Tests for specparam.plts.time."""

from pytest import raises

from specparam import SpectralTimeModel
from specparam.modutils.errors import NoModelError

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.time import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_time(tft, skip_if_no_mpl):

    plot_time_model(tft, file_path=TEST_PLOTS_PATH, file_name='test_plot_time.png')

    # Test error if no data available to plot
    ntft = SpectralTimeModel()
    with raises(NoModelError):
        ntft.plot()
