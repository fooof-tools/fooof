"""Tests for fooof.plts.fm."""

from fooof.plts.fg import *
from fooof.tests.utils import plot_test

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fg(tfg, skip_if_no_mpl):

    plot_fg(tfg)

@plot_test
def test_plot_fg_bg(tfg, skip_if_no_mpl):

    plot_fg_bg(tfg)

@plot_test
def test_plot_fg_gf(tfg, skip_if_no_mpl):

    plot_fg_gf(tfg)

@plot_test
def test_plot_fg_osc_cens(tfg, skip_if_no_mpl):

    plot_fg_osc_cens(tfg)
