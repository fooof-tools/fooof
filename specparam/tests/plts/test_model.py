"""Tests for specparam.plts.model."""

from specparam.tests.tutils import plot_test
from specparam.tests.settings import TEST_PLOTS_PATH

from specparam.plts.model import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_model(tfm, skip_if_no_mpl):

    # Make sure model has been fit
    tfm.fit()

    plot_model(tfm, file_path=TEST_PLOTS_PATH, file_name='test_plot_model.png')

@plot_test
def test_plot_model_add_peaks(tfm, skip_if_no_mpl):

    # Make sure model has been fit
    tfm.fit()

    # Test run each of the add peak approaches
    for add_peak in ['shade', 'dot', 'outline', 'line', 'shade-dot', 'outline-line']:
        file_name = 'test_plot_model_add_peaks_' + add_peak + '.png'
        plot_model(tfm, plot_peaks=add_peak, file_path=TEST_PLOTS_PATH, file_name=file_name)
