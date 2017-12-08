"""Test functions for FOOOF plots."""

import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt

from fooof.plts import *

###################################################################################################
###################################################################################################

def test_plot_scatter_1():

	plt.close('all')

	dat = np.random.randint(0, 100, 100)

	plot_scatter_1(dat, 'label', 'title')

	ax = plt.gca()
	assert ax.has_data()

def test_plot_scatter_2():

	plt.close('all')

	dat1 = np.random.randint(0, 100, 100)
	dat2 = np.random.randint(0, 100, 100)

	plot_scatter_2(dat1, 'label1', dat2, 'label2', 'title')

	ax = plt.gca()
	assert ax.has_data()

def test_plot_hist():

	plt.close('all')

	dat = np.random.randint(0, 100, 100)
	plot_hist(dat, 'label', 'title')

	ax = plt.gca()
	assert ax.has_data()
