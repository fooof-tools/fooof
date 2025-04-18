"""Tests for specparam.plts.aperiodic."""

import numpy as np

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.aperiodic import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_aperiodic_params(skip_if_no_mpl):

    # Test for 'fixed' mode: offset, exponent
    aps = np.array([[1, 1], [0.5, 0.5], [2, 2]])
    plot_aperiodic_params(aps)

    # Test for multiple inputs
    plot_aperiodic_params([aps, aps])

    # Test for 'knee' mode: offset, knee exponent
    aps = np.array([[1, 100, 1], [0.5, 150, 0.5], [2, 200, 2]])
    plot_aperiodic_params(aps,
                          file_path=TEST_PLOTS_PATH, file_name='test_plot_aperiodic_params.png')

@plot_test
def test_plot_aperiodic_fits(skip_if_no_mpl):

    aps = np.array([[1, 1], [0.5, 0.5], [2, 2]])

    # Test for single group input
    plot_aperiodic_fits(aps, [1, 50], 'fixed', control_offset=True)

    # Test for multiple input
    plot_aperiodic_fits([aps, aps], [1, 50], 'fixed', control_offset=True)

    # Test for 'knee' mode: offset, knee exponent
    aps = np.array([[1, 100, 1], [0.5, 150, 0.5], [2, 200, 2]])
    plot_aperiodic_fits(aps, [1, 50], 'knee',
                        file_path=TEST_PLOTS_PATH, file_name='test_plot_aperiodic_fits.png')
