"""Test functions for specparam.data.bands."""

from pytest import raises

from specparam.bands.bands import *

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

def test_bands_eq():

    bands1 = Bands({'alpha' : (7, 14)})
    bands2 = Bands({'alpha' : (7, 14)})

    assert bands1 == bands2

def test_bands_dunders(tbands):

    assert tbands['theta']
    assert repr(tbands)
    assert len(tbands) == 3

def test_bands_properties(tbands):

    assert set(tbands.labels) == set(['theta', 'alpha', 'beta'])
    assert tbands.n_bands == 3

def test_bands_n_bands():

    n_bands = 2
    bands = Bands(n_bands=n_bands)
    assert bands.bands == {}
    assert bands._n_bands == n_bands
    assert len(bands) == n_bands

    # Check that adding a band replaces n_band definition
    bands.add_band('alpha', [7, 14])
    assert bands._n_bands == None
    assert len(bands) == 1

    # test fails adding both bands and n_bands
    with raises(ValueError):
        bands = Bands({'alpha' : (7, 14)}, n_bands=2)


def test_check_bands(tbands):

    out1 = check_bands(tbands)
    assert isinstance(out1, Bands)
    assert out1 == tbands

    out2 = check_bands({'alpha' : (7, 14)})
    assert isinstance(out2, Bands)

    out3 = check_bands(2)
    assert isinstance(out3, Bands)
