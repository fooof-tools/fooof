"""Tests for specparam.objs.base, including the base object and it's methods."""

from specparam.core.items import OBJ_DESC
from specparam.data import ModelRunModes

from specparam.objs.base import *

###################################################################################################
###################################################################################################

## Common Base Object

def test_common_base():

    tobj = CommonBase()
    assert isinstance(tobj, CommonBase)

def test_common_base_copy():

    tobj = CommonBase()
    ntobj = tobj.copy()

    assert ntobj != tobj

## 1D Base Object

def test_base():

    tobj = BaseObject()
    assert isinstance(tobj, CommonBase)
    assert isinstance(tobj, BaseObject)

def test_base_run_modes():

    tobj = BaseObject()
    tobj.set_run_modes(False, False, False)
    run_modes = tobj.get_run_modes()
    assert isinstance(run_modes, ModelRunModes)

    for run_mode in OBJ_DESC['run_modes']:
        assert getattr(tobj, run_mode) is False
        assert getattr(run_modes, run_mode.strip('_')) is False

## 2D Base Object

def test_base2d():

    tobj2d = BaseObject2D()
    assert isinstance(tobj2d, CommonBase)
    assert isinstance(tobj2d, BaseObject2D)
    assert isinstance(tobj2d, BaseResults2D)
    assert isinstance(tobj2d, BaseObject2D)

## 2DT Base Object

def test_base2dt():

    tobj2dt = BaseObject2DT()
    assert isinstance(tobj2dt, CommonBase)
    assert isinstance(tobj2dt, BaseObject2DT)
    assert isinstance(tobj2dt, BaseResults2DT)
    assert isinstance(tobj2dt, BaseObject2DT)

## 3D Base Object

def test_base3d():

    tobj3d = BaseObject3D()
    assert isinstance(tobj3d, CommonBase)
    assert isinstance(tobj3d, BaseObject2DT)
    assert isinstance(tobj3d, BaseResults2DT)
    assert isinstance(tobj3d, BaseObject2DT)
    assert isinstance(tobj3d, BaseObject3D)
