"""Tests for fooof.plts.error."""

from pytest import raises, mark, param

import numpy as np

from fooof.tests.tutils import plot_test

from fooof.plts.error import *

###################################################################################################
###################################################################################################

@plot_test
def test_plot_spectral_error(skip_if_no_mpl):

    fs = np.arange(3, 41, 1)
    errs = np.ones(len(fs))

    plot_spectral_error(fs, errs)


@plot_test
def test_plot_error_shade(skip_if_no_mpl, tfg):

    freqs = tfg.freqs
    powers = tfg.power_spectra

    # Invalid 1d array, without shade
    with raises(ValueError):
        plot_error_shade(freqs, powers[0])

    # Valid 1d array with shade
    plot_error_shade(freqs, np.mean(powers, axis=0), shade=np.std(powers, axis=0))

    # 2d array
    plot_error_shade(freqs, powers)
