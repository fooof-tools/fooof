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
