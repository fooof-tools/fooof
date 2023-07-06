"""Tests for fooof.plts.error."""

import numpy as np

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

from fooof.plts.error import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectral_error(skip_if_no_mpl):

    fs = np.arange(3, 41, 1)
    errs = np.ones(len(fs))

    plot_spectral_error(fs, errs, save_fig=True, file_path=TEST_PLOTS_PATH,
                        file_name='test_plot_spectral_error.png')
