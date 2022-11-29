"""Test functions for fooof.data.bands."""

from pytest import raises

from fooof.bands.bands import *

###################################################################################################
###################################################################################################

def test_bands():

    bands = Bands()
    assert isinstance(bands, Bands)

def test_bands_add_band():

    bands = Bands()
    bands.add_band('test', (5, 10))
    assert bands.bands == {'test' : (5, 10)}

def test_bands_remove_band():

    bands = Bands()
    bands.add_band('test', (5, 10))
    bands.remove_band('test')
    assert bands.bands == {}

def test_bands_errors():

    bands = Bands()
    with raises(ValueError):
        bands.add_band(1, (1, 1))
    with raises(ValueError):
        bands.add_band('test', (1, 1, 1))
    with raises(ValueError):
        bands.add_band('test', (2, 1))

def test_bands_dunders(tbands):

    assert tbands['theta']
    assert tbands.alpha
    assert repr(tbands)
    assert len(tbands) == 3

def test_bands_properties(tbands):

    assert set(tbands.labels) == set(['theta', 'alpha', 'beta'])
    assert tbands.n_bands == 3
