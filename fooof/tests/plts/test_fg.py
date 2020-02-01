"""Tests for fooof.plts.fg."""

from py.test import raises

from fooof import FOOOFGroup
from fooof.core.errors import NoModelError

from fooof.plts.fg import *
from fooof.tests.test_utils import plot_test

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fg(tfg, skip_if_no_mpl):

    plot_fg(tfg)

    # Test error if no data available to plot
    tfg = FOOOFGroup()
    with raises(NoModelError):
        tfg.plot()

@plot_test
def test_plot_fg_ap(tfg, skip_if_no_mpl):

    plot_fg_ap(tfg)

@plot_test
def test_plot_fg_gf(tfg, skip_if_no_mpl):

    plot_fg_gf(tfg)

@plot_test
def test_plot_fg_peak_cens(tfg, skip_if_no_mpl):

    plot_fg_peak_cens(tfg)
