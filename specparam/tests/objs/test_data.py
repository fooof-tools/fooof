"""Tests for specparam.objs.data, including the data object and it's methods."""

from specparam.data import SpectrumMetaData

from specparam.tests.tutils import plot_test

from specparam.objs.data import *

###################################################################################################
###################################################################################################

## 1D Data Object

def test_base_data():
    """Check base object initializes properly."""

    tdata = BaseData()
    assert tdata

def test_base_data_add_data():

    tdata = BaseData()
    freqs, pows = np.array([1, 2, 3]), np.array([10, 10, 10])
    tdata.add_data(freqs, pows)
    assert tdata.has_data

def test_base_data_meta_data():

    tdata = BaseData()

    # Test adding meta data
    meta_data = SpectrumMetaData([3, 40], 0.5)
    tdata.add_meta_data(meta_data)
    for mlabel in OBJ_DESC['meta_data']:
        assert getattr(tdata, mlabel) == getattr(meta_data, mlabel)

    # Test getting meta data
    meta_data_out = tdata.get_meta_data()
    assert isinstance(meta_data_out, SpectrumMetaData)
    assert meta_data_out == meta_data

def test_base_data_set_check_modes(tdata):

    tdata.set_check_modes(False, False)
    assert tdata._check_freqs is False
    assert tdata._check_data is False

    tdata.set_check_modes(True, True)
    assert tdata._check_freqs is True
    assert tdata._check_data is True

@plot_test
def test_base_data_plot(tdata, skip_if_no_mpl):

    tdata.plot()

## 2D Data Object

def test_base_data2d():

    tdata2d = BaseData2D()
    assert tdata2d
    assert isinstance(tdata2d, BaseData)
    assert isinstance(tdata2d, BaseData2D)

def test_base_data2d_add_data():

    tdata2d = BaseData2D()
    freqs, pows = np.array([1, 2, 3]), np.array([[10, 10, 10], [20, 20, 20]])
    tdata2d.add_data(freqs, pows)
    assert tdata2d.has_data

@plot_test
def test_base_data2d_plot(tdata2d, skip_if_no_mpl):

    tdata2d.plot()

## 2DT Data Object

def test_base_data2dt():

    tdata2dt = BaseData2DT()
    assert tdata2dt
    assert isinstance(tdata2dt, BaseData)
    assert isinstance(tdata2dt, BaseData2D)
    assert isinstance(tdata2dt, BaseData2DT)

def test_base_data2dt_add_data():

    tdata2dt = BaseData2DT()
    freqs, pows = np.array([1, 2, 3]), np.array([[10, 10, 10], [20, 20, 20]]).T
    tdata2dt.add_data(freqs, pows)
    assert tdata2dt.has_data
    assert np.all(tdata2dt.spectrogram)
    assert tdata2dt.n_time_windows

## 3D Data Object

def test_base_data3d():

    tdata3d = BaseData3D()
    assert tdata3d
    assert isinstance(tdata3d, BaseData)
    assert isinstance(tdata3d, BaseData2D)
    assert isinstance(tdata3d, BaseData2DT)
    assert isinstance(tdata3d, BaseData3D)

def test_base_data3d_add_data():

    tdata3d = BaseData3D()
    freqs, pows = np.array([1, 2, 3]), np.array([[10, 10, 10], [20, 20, 20]]).T
    tdata3d.add_data(freqs, np.array([pows, pows]))
    assert tdata3d.has_data
    assert np.all(tdata3d.spectrograms)
    assert tdata3d.n_events
