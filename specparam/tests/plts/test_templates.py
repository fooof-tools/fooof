"""Tests for specparam.plts.templates."""

import numpy as np

from specparam.modutils.dependencies import safe_import

from specparam.tests.tutils import plot_test

from specparam.plts.templates import *

mpl = safe_import('matplotlib')

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

@plot_test
def test_plot_yshade(skip_if_no_mpl):

    xs = np.array([1, 2, 3])
    ys = np.array([[1, 2, 3], [2, 3, 4]])
    plot_yshade(xs, ys)

@plot_test
def test_plot_param_over_time(skip_if_no_mpl):

    param = np.array([1, 2, 3, 2, 1, 2, 4, 2, 3, 2, 1])

    plot_param_over_time(None, param, label='param', color='red')

@plot_test
def test_plot_params_over_time(skip_if_no_mpl):

    params = [np.array([1, 2, 3, 2, 1, 2, 4, 2, 3, 2, 1]),
              np.array([2, 3, 2, 1, 2, 4, 2, 3, 2, 1, 2])]

    plot_params_over_time(None, params, labels=['param1', 'param2'], colors=['blue', 'red'])

@plot_test
def test_plot_param_over_time_yshade(skip_if_no_mpl):

    params = np.array([[1, 2, 3, 2, 1, 2, 4, 2, 3, 2, 1],
                       [2, 3, 2, 1, 2, 4, 2, 3, 2, 1, 2]])
    plot_param_over_time_yshade(None, params)

def test_plot_text(skip_if_no_mpl):

    text = 'This is a string.'
    plot_text(text, 0.5, 0.5)

    # Test this plot custom, as text doesn't count as data
    ax = mpl.pyplot.gca()
    assert isinstance(ax.get_children()[0], mpl.text.Text)
