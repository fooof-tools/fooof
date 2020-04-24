"""Tests for fooof.plts.spectra."""

import numpy as np

from fooof.tests.tutils import plot_test

from fooof.plts.spectra import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectrum(tfm, skip_if_no_mpl):

    plot_spectrum(tfm.freqs, tfm.power_spectrum)

    # Test with logging both axes
    plot_spectrum(tfm.freqs, tfm.power_spectrum, True, True)

@plot_test
def test_plot_spectra(tfg, skip_if_no_mpl):

    # Test with 1d inputs - 1d freq array and list of 1d power spectra
    plot_spectra(tfg.freqs, [tfg.power_spectra[0, :], tfg.power_spectra[1, :]])

    # Test with multiple freq inputs - list of 1d freq array and list of 1d power spectra
    plot_spectra([tfg.freqs, tfg.freqs], [tfg.power_spectra[0, :], tfg.power_spectra[1, :]])

    # Test with 2d array inputs
    plot_spectra(np.vstack([tfg.freqs, tfg.freqs]),
                 np.vstack([tfg.power_spectra[0, :], tfg.power_spectra[1, :]]))

    # Test with labels
    plot_spectra(tfg.freqs, [tfg.power_spectra[0, :], tfg.power_spectra[1, :]], labels=['A', 'B'])

@plot_test
def test_plot_spectrum_shading(tfm, skip_if_no_mpl):

    plot_spectrum_shading(tfm.freqs, tfm.power_spectrum, shades=[8, 12], add_center=True)

@plot_test
def test_plot_spectra_shading(tfg, skip_if_no_mpl):

    plot_spectra_shading(tfg.freqs, [tfg.power_spectra[0, :], tfg.power_spectra[1, :]],
                         shades=[8, 12], add_center=True)

    # Test with **kwargs that pass into plot_spectra
    plot_spectra_shading(tfg.freqs, [tfg.power_spectra[0, :], tfg.power_spectra[1, :]],
                         shades=[8, 12], add_center=True, log_freqs=True, log_powers=True,
                         labels=['A', 'B'])
