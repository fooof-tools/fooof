"""Tests for specparam.plts.compare."""

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.compare import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_model_comparison(tmodelcomp, skip_if_no_mpl):

    plot_model_comparison(tmodelcomp)
