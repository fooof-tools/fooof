"""Tests for FOOOF core.modutils."""

from fooof.core.modutils import *

###################################################################################################
###################################################################################################

def test_get_obj_desc():

    assert get_obj_desc()

def test_docs_drop_param():

    ds = """STUFF

    Parameters
    ----------
    first : thing
        xx
    second : stuff
        xx

    Returns
    -------
    out : yay
        xx
    """

    out = docs_drop_param(ds)
    assert 'first' not in out
    assert 'second' in out
