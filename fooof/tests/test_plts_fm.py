"""Tests for fooof.plts.fm."""

from fooof.plts.fm import *

###################################################################################################
###################################################################################################

def test_plot_fm(tfm):

    plt.close('all')

    plot_fm(tfm)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_osc_iter(tfm):

    plt.close('all')

    plot_osc_iter(tfm)

    ax = plt.gca()
    assert ax.has_data()
