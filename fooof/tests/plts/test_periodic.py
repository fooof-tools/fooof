"""Tests for fooof.plts.periodic."""

import numpy as np

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

from fooof.plts.periodic import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_peak_params(skip_if_no_mpl):

    peaks = np.array([[6, 1, 2], [10, 2, 1.5], [25, 1.5, 3]])

    # Test with a single set of params
    plot_peak_params(peaks)

    # Test with multiple set of params
    plot_peak_params([peaks, peaks], save_fig=True, file_path=TEST_PLOTS_PATH,
                     file_name='test_plot_peak_params.png')

@plot_test
def test_plot_peak_fits(skip_if_no_mpl):

    peaks = np.array([[6, 1, 2], [10, 2, 1.5], [25, 1.5, 3]])

    # Test with a single set of params
    plot_peak_fits(peaks)

    # Test with multiple set of params
    plot_peak_fits([peaks, peaks], save_fig=True, file_path=TEST_PLOTS_PATH,
                   file_name='test_plot_peak_fits.png')
