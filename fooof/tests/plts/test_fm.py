"""Tests for fooof.plts.fm."""

from fooof.tests.tutils import plot_test

from fooof.plts.fm import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fm(tfm, skip_if_no_mpl):

    # Make sure model has been fit
    tfm.fit()

    plot_fm(tfm)

@plot_test
def test_plot_fm_add_peaks(tfm, skip_if_no_mpl):

    # Make sure model has been fit
    tfm.fit()

    # Test run each of the add peak approaches
    for add_peak in ['shade', 'dot', 'outline', 'line']:
        plot_fm(tfm, plot_peaks=add_peak)

    # Test run some combinations
    for add_peak in ['shade-dot', 'outline-line']:
        plot_fm(tfm, plot_peaks=add_peak)
