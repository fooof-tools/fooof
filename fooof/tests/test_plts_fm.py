"""Tests for fooof.plts.fm."""

from py.test import raises

from fooof import FOOOF
from fooof.plts.fm import *
from fooof.tests.utils import plot_test

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fm(tfm, skip_if_no_mpl):

    plot_fm(tfm)

def test_plot_fm_error(skip_if_no_mpl):

    # Check raises error with no data
    tfm = FOOOF()
    with raises(RuntimeError):
        tfm.plot()

@plot_test
def test_plot_peak_iter(tfm, skip_if_no_mpl):

    plot_peak_iter(tfm)
