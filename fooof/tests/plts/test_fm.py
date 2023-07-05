"""Tests for fooof.plts.fm."""

import numpy as np

from fooof.tests.tutils import plot_test
from fooof.tests.settings import TEST_PLOTS_PATH

from fooof.plts.fm import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_fm(tfm, skip_if_no_mpl):

    # Make sure model has been fit
    tfm.fit()

    plot_fm(tfm, save_fig=True, file_path=TEST_PLOTS_PATH,
            file_name='test_plot_fm.png')

@plot_test
def test_plot_fm_custom(tfm, skip_if_no_mpl):

    # Extract broader range of data available in the object
    custom_freqs = tfm.freqs
    custom_power_spectrum = np.power(10, tfm.power_spectrum)

    # Make sure model has been fit - set custom frequency range
    tfm.fit(custom_freqs, custom_power_spectrum, freq_range=[5, 35])

    plot_fm(tfm, freqs=custom_freqs, power_spectrum=custom_power_spectrum,
            freq_range=[1, 55], save_fig=True, file_path=TEST_PLOTS_PATH,
            file_name='test_plot_fm_custom.png')

@plot_test
def test_plot_fm_add_peaks(tfm, skip_if_no_mpl):

    # Make sure model has been fit
    tfm.fit()

    # Test run each of the add peak approaches
    for add_peak in ['shade', 'dot', 'outline', 'line', 'shade-dot', 'outline-line']:
        file_name = 'test_plot_fm_add_peaks_' + add_peak + '.png'
        plot_fm(tfm, plot_peaks=add_peak, save_fig=True,
                file_path=TEST_PLOTS_PATH, file_name=file_name)
