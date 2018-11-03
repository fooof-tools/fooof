"""Tests for fooof.plts.spectra."""

from fooof.tests.utils import plot_test
from fooof.plts.spectra import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectra(tfg, skip_if_no_mpl):

    plot_spectra(tfg.freqs, [tfg.power_spectra[0, :], tfg.power_spectra[1, :]])

@plot_test
def test_plot_spectrum_shading(tfm, skip_if_no_mpl):

    plot_spectrum_shading(tfm.freqs, tfm.power_spectrum, shades=[8, 12], add_center=True)

@plot_test
def test_plot_spectra_shading(tfg, skip_if_no_mpl):

    plot_spectra_shading(tfg.freqs, [tfg.power_spectra[0, :], tfg.power_spectra[1, :]],
                         shades=[8, 12], add_center=True)
