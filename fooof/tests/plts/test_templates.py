"""Tests for fooof.plts.templates."""

import numpy as np

from fooof.tests.tutils import plot_test

from fooof.plts.templates import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_scatter_1(skip_if_no_mpl):

    data = np.random.randint(0, 100, 100)

    plot_scatter_1(data, 'label', 'title')

@plot_test
def test_plot_scatter_2(skip_if_no_mpl):

    data1 = np.random.randint(0, 100, 100)
    data2 = np.random.randint(0, 100, 100)

    plot_scatter_2(data1, 'label1', data2, 'label2', 'title')

@plot_test
def test_plot_hist(skip_if_no_mpl):

    data = np.random.randint(0, 100, 100)
    plot_hist(data, 'label', 'title')
