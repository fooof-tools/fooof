"""Tests for fooof.plts.fm."""

from fooof.plts.fm import *
from fooof.tests.utils import plot_test

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fm(tfm, skip_if_no_mpl):

    plot_fm(tfm)

@plot_test
def test_plot_fm_peak_iter(tfm, skip_if_no_mpl):

    plot_fm_peak_iter(tfm)
