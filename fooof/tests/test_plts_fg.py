"""Tests for fooof.plts.fm."""

from py.test import raises

from fooof import FOOOFGroup
from fooof.plts.fg import *
from fooof.tests.utils import plot_test

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fg(tfg, skip_if_no_mpl):

    plot_fg(tfg)

def test_plot_fg_error(skip_if_no_mpl):

    tfg = FOOOFGroup()

    with raises(RuntimeError):
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
