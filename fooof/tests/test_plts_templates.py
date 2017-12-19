"""Test functions for FOOOF plots."""

import numpy as np

from fooof.plts.templates import *

###################################################################################################
###################################################################################################

def test_plot_psd(skip_if_no_mpl):

    plt.close('all')

    dat1 = np.random.randint(0, 100, 100)
    dat2 = np.random.randint(0, 100, 100)

    plot_psd(dat1, dat2, True)

    ax = plt.gca()
    assert ax.has_data()

def test_plot_scatter_1(skip_if_no_mpl):

    plt.close('all')

    dat = np.random.randint(0, 100, 100)

    plot_scatter_1(dat, 'label', 'title')

    ax = plt.gca()
    assert ax.has_data()

def test_plot_scatter_2(skip_if_no_mpl):

    plt.close('all')

    dat1 = np.random.randint(0, 100, 100)
    dat2 = np.random.randint(0, 100, 100)

    plot_scatter_2(dat1, 'label1', dat2, 'label2', 'title')

    ax = plt.gca()
    assert ax.has_data()

def test_plot_hist(skip_if_no_mpl):

    plt.close('all')

    dat = np.random.randint(0, 100, 100)
    plot_hist(dat, 'label', 'title')

    ax = plt.gca()
    assert ax.has_data()
