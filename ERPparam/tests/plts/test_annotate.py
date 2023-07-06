"""Tests for fooof.plts.annotate."""

import numpy as np

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

from fooof.plts.annotate import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_annotated_peak_search(tfm, skip_if_no_mpl):

    plot_annotated_peak_search(tfm, save_fig=True, file_path=TEST_PLOTS_PATH,
                               file_name='test_plot_annotated_peak_search.png')

@plot_test
def test_plot_annotated_model(tfm, skip_if_no_mpl):

    # Make sure model has been fit & then plot annotated model
    tfm.fit()
    plot_annotated_model(tfm, save_fig=True, file_path=TEST_PLOTS_PATH,
                         file_name='test_plot_annotated_model.png')
