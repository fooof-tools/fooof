"""Tests for specparam.plts.spectra."""

from pytest import raises

import numpy as np

from specparam.tests.tutils import plot_test
from specparam.tests.tsettings import TEST_PLOTS_PATH

from specparam.plts.spectra import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectra(tfm, tfg, skip_if_no_mpl):

    # Test with 1d inputs - 1d freq array & list of 1d power spectra
    plot_spectra(tfm.data.freqs, tfm.data.power_spectrum,
                 file_path=TEST_PLOTS_PATH, file_name='test_plot_spectra_1d.png')

    # Test with 1d inputs - 1d freq array & list of 1d power spectra
    plot_spectra(tfg.data.freqs, [tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :]],
                 file_path=TEST_PLOTS_PATH, file_name='test_plot_spectra_list_1d.png')

    # Test with multiple freq inputs - list of 1d freq array and list of 1d power spectra
    plot_spectra([tfg.data.freqs, tfg.data.freqs],
                 [tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :]],
                 file_path=TEST_PLOTS_PATH, file_name='test_plot_spectra_list_1d_freqs.png')

    # Test with multiple lists - list of 1d freqs & list of 1d power spectra (different f ranges)
    plot_spectra([tfg.data.freqs, tfg.data.freqs[:-5]],
                 [tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :-5]],
                 file_path=TEST_PLOTS_PATH, file_name='test_plot_spectra_lists_1d.png')

    # Test with 2d array inputs
    plot_spectra(np.vstack([tfg.data.freqs, tfg.data.freqs]),
                 np.vstack([tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :]]),
                 file_path=TEST_PLOTS_PATH, file_name='test_plot_spectra_2d.png')

    # Test with labels
    plot_spectra(tfg.data.freqs,
                 [tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :]], labels=['A', 'B'],
                 file_path=TEST_PLOTS_PATH, file_name='test_plot_spectra_labels.png')

@plot_test
def test_plot_spectra_shading(tfm, tfg, skip_if_no_mpl):

    plot_spectra_shading(tfm.data.freqs, tfm.data.power_spectrum, shades=[8, 12], add_center=True,
                         file_path=TEST_PLOTS_PATH,
                         file_name='test_plot_spectrum_shading1.png')

    plot_spectra_shading(tfg.data.freqs,
                         [tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :]],
                         shades=[8, 12], add_center=True, file_path=TEST_PLOTS_PATH,
                         file_name='test_plot_spectra_shading2.png')

    # Test with **kwargs that pass into plot_spectra
    plot_spectra_shading(tfg.data.freqs,
                         [tfg.data.power_spectra[0, :], tfg.data.power_spectra[1, :]],
                         shades=[8, 12], add_center=True, log_freqs=True, log_powers=True,
                         labels=['A', 'B'], file_path=TEST_PLOTS_PATH,
                         file_name='test_plot_spectra_shading_kwargs.png')

@plot_test
def test_plot_spectra_yshade(skip_if_no_mpl, tfg):

    freqs = tfg.data.freqs
    powers = tfg.data.power_spectra

    # Invalid 1d array, without shade
    with raises(ValueError):
        plot_spectra_yshade(freqs, powers[0])

    # Plot with 2d array
    plot_spectra_yshade(freqs, powers, shade='std',
                        file_path=TEST_PLOTS_PATH,
                        file_name='test_plot_spectra_yshade1.png')

    # Plot shade with given 1d array
    plot_spectra_yshade(freqs, np.mean(powers, axis=0),
                        shade=np.std(powers, axis=0),
                        file_path=TEST_PLOTS_PATH,
                        file_name='test_plot_spectra_yshade2.png')

    # Plot shade with different average and shade approaches
    plot_spectra_yshade(freqs, powers, shade='sem', average='median',
                        file_path=TEST_PLOTS_PATH,
                        file_name='test_plot_spectra_yshade3.png')

@plot_test
def test_plot_spectrogram(skip_if_no_mpl, tft):

    freqs = tft.data.freqs
    spectrogram = np.tile(tft.data.power_spectra.T, 50)

    plot_spectrogram(freqs, spectrogram,
                     file_path=TEST_PLOTS_PATH, file_name='test_plot_spectrogram.png')
