"""Tests for specparam.modutils.dependencies."""

from pytest import raises

from specparam.modutils.dependencies import *

###################################################################################################
###################################################################################################

def test_safe_import():

    np = safe_import('numpy')
    assert np

    bad = safe_import('bad')
    assert not bad

def test_check_dependency():

    import numpy as np
    @check_dependency(np, 'numpy')
    def subfunc_good():
        pass
    subfunc_good()

    bad = None
    @check_dependency(bad, 'bad')
    def subfunc_bad():
        pass
    with raises(ImportError):
        subfunc_bad()
