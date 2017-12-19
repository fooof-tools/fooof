"""Tests for fooof.plts.fm."""

from fooof.plts.fg import *

###################################################################################################
###################################################################################################

def test_plot_fg(tfg, skip_if_no_mpl):

    plt.close('all')

    plot_fg(tfg)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_fg_bg(tfg, skip_if_no_mpl):

    plt.close('all')

    plot_fg_bg(tfg)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_fg_gf(tfg, skip_if_no_mpl):

    plt.close('all')

    plot_fg_gf(tfg)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_fg_osc_cens(tfg, skip_if_no_mpl):

    plt.close('all')

    plot_fg_osc_cens(tfg)

    ax = plt.gca()
    assert ax.has_data()
