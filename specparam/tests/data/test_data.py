"""Tests for specparam.data.data."""

from specparam.data import SpectrumMetaData, ModelChecks

from specparam.tests.tutils import plot_test

from specparam.data.data import *

###################################################################################################
###################################################################################################

## 1D Data Object

def test_data():
    """Check data object initializes properly."""

    tdata = Data()
    assert tdata
    assert not tdata.has_data
    assert not tdata.n_freqs

def test_data_add_data():

    tdata = Data()
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])
    tdata.add_data(freqs, pows)
    assert tdata.has_data
    assert tdata.n_freqs == len(freqs)

def test_data_meta_data():

    tdata = Data()

    # Test adding meta data
    meta_data = SpectrumMetaData([3, 40], 0.5)
    tdata.add_meta_data(meta_data)
    for mlabel in tdata._meta_fields:
        assert getattr(tdata, mlabel) == getattr(meta_data, mlabel)

    # Test getting meta data
    meta_data_out = tdata.get_meta_data()
    assert isinstance(meta_data_out, SpectrumMetaData)
    assert meta_data_out == meta_data

def test_data_get_set_checks(tdata):

    tdata.set_checks(False, False)
    tchecks1 = tdata.get_checks()
    assert isinstance(tchecks1, ModelChecks)
    assert tdata.checks['freqs'] == tchecks1.check_freqs == False
    assert tdata.checks['data'] == tchecks1.check_data == False

    tdata.set_checks(True, True)
    tchecks2 = tdata.get_checks()
    assert isinstance(tchecks2, ModelChecks)
    assert tdata.checks['freqs'] == tchecks2.check_freqs == True
    assert tdata.checks['data'] == tchecks2.check_data == True

@plot_test
def test_data_plot(tdata, skip_if_no_mpl):

    tdata.plot()

## 2D Data Object

def test_data2d():

    tdata2d = Data2D()
    assert tdata2d
    assert isinstance(tdata2d, Data)
    assert isinstance(tdata2d, Data2D)
    assert not tdata2d.has_data

def test_data2d_add_data():

    tdata2d = Data2D()
    freqs, pows = np.array([1, 2, 3]), np.array([[10, 10, 10], [20, 20, 20]])
    tdata2d.add_data(freqs, pows)
    assert tdata2d.has_data
    assert tdata2d.n_spectra == len(pows)

@plot_test
def test_data2d_plot(tdata2d, skip_if_no_mpl):

    tdata2d.plot()

## 2DT Data Object

def test_data2dt():

    tdata2dt = Data2DT()
    assert tdata2dt
    assert isinstance(tdata2dt, Data)
    assert isinstance(tdata2dt, Data2D)
    assert isinstance(tdata2dt, Data2DT)
    assert not tdata2dt.has_data

def test_data2dt_add_data():

    tdata2dt = Data2DT()
    freqs, pows = np.array([1, 2, 3]), np.array([[10, 10, 10], [20, 20, 20]]).T
    tdata2dt.add_data(freqs, pows)
    assert tdata2dt.has_data
    assert np.all(tdata2dt.spectrogram)
    assert tdata2dt.n_spectra == tdata2dt.n_time_windows == len(pows.T)

## 3D Data Object

def test_data3d():

    tdata3d = Data3D()
    assert tdata3d
    assert isinstance(tdata3d, Data)
    assert isinstance(tdata3d, Data2D)
    assert isinstance(tdata3d, Data2DT)
    assert isinstance(tdata3d, Data3D)
    assert not tdata3d.has_data

def test_data3d_add_data():

    tdata3d = Data3D()
    freqs, pows = np.array([1, 2, 3]), np.array([[10, 10, 10], [20, 20, 20]]).T
    tdata3d.add_data(freqs, np.array([pows, pows]))
    assert tdata3d.has_data
    assert np.all(tdata3d.spectrograms)
    assert tdata3d.n_events
    assert tdata3d.n_spectra == 2 * len(pows.T)
