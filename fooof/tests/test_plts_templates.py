"""Test functions for FOOOF plots."""

import numpy as np

from fooof.plts.templates import *
from fooof.tests.utils import plot_test

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectrum(skip_if_no_mpl):


    dat1 = np.random.randint(1, 100, 100)
    dat2 = np.random.randint(1, 100, 100)

    plot_spectrum(dat1, dat2, True)

@plot_test
def test_plot_scatter_1(skip_if_no_mpl):

    dat = np.random.randint(0, 100, 100)

    plot_scatter_1(dat, 'label', 'title')

@plot_test
def test_plot_scatter_2(skip_if_no_mpl):

    plt.close('all')

    dat1 = np.random.randint(0, 100, 100)
    dat2 = np.random.randint(0, 100, 100)

    plot_scatter_2(dat1, 'label1', dat2, 'label2', 'title')

    ax = plt.gca()
    assert ax.has_data()

@plot_test
def test_plot_hist(skip_if_no_mpl):

    dat = np.random.randint(0, 100, 100)
    plot_hist(dat, 'label', 'title')
