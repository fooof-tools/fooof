"""Tests for specparam.objs.base, including the base object and it's methods."""

from specparam.modes.items import OBJ_DESC

from specparam.objs.base import *

###################################################################################################
###################################################################################################

## Common Base Object

def test_common_base():

    tobj = CommonBase(verbose=False)
    assert isinstance(tobj, CommonBase)

def test_common_base_copy():

    tobj = CommonBase(verbose=False)
    ntobj = tobj.copy()

    assert ntobj != tobj

## 1D Base Object

def test_base():

    tobj = BaseObject()
    assert isinstance(tobj, CommonBase)
    assert isinstance(tobj, BaseObject)

## 2D Base Object

def test_base2d():

    tobj2d = BaseObject2D()
    assert isinstance(tobj2d, CommonBase)
    assert isinstance(tobj2d, BaseObject2D)

## 2DT Base Object

def test_base2dt():

    tobj2dt = BaseObject2DT()
    assert isinstance(tobj2dt, CommonBase)
    assert isinstance(tobj2dt, BaseObject2DT)

## 3D Base Object

def test_base3d():

    tobj3d = BaseObject3D()
    assert isinstance(tobj3d, CommonBase)
    assert isinstance(tobj3d, BaseObject2DT)
    assert isinstance(tobj3d, BaseObject3D)
