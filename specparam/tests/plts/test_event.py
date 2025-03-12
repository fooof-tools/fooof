"""Tests for specparam.plts.event."""

from pytest import raises

from specparam import SpectralTimeEventModel
from specparam.modutils.errors import NoModelError

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.event import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_event(tfe, skip_if_no_mpl):

    plot_event_model(tfe, file_path=TEST_PLOTS_PATH, file_name='test_plot_event.png')

    # Test error if no data available to plot
    ntfe = SpectralTimeEventModel()
    with raises(NoModelError):
        ntfe.plot()
