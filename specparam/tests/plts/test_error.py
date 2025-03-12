"""Tests for specparam.plts.error."""

import numpy as np

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.error import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectral_error(skip_if_no_mpl):

    fs = np.arange(3, 41, 1)
    errs = np.ones(len(fs))

    plot_spectral_error(fs, errs, file_path=TEST_PLOTS_PATH,
                        file_name='test_plot_spectral_error.png')
