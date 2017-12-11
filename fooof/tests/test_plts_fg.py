"""Tests for fooof.plts.fm."""

from fooof.plts.fg import *

###################################################################################################
###################################################################################################

def test_plot_fg(tfg):

    plt.close('all')

    plot_fg(tfg)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_fg_bg(tfg):

    plt.close('all')

    plot_fg_bg(tfg)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_fg_gf(tfg):

    plt.close('all')

    plot_fg_gf(tfg)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_fg_osc_cens(tfg):

    plt.close('all')

    plot_fg_osc_cens(tfg)

    ax = plt.gca()
    assert ax.has_data()
