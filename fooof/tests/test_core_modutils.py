"""Tests for FOOOF core.modutils.

Note: decorators (that are in modutils) are currently not tested.
"""

from fooof import FOOOF
from fooof.core.modutils import *

###################################################################################################
###################################################################################################

def test_safe_import():

    np = safe_import('numpy')
    assert np

    bad = safe_import('bad')
    assert not bad

def test_get_obj_desc():

    desc =  get_obj_desc()

    tfm = FOOOF()
    objs = dir(tfm)

    # Test that everything in dict is a valid component of the fooof object
    for ke, va in desc.items():
        for it in va:
            assert it in objs

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

def test_docs_append_to_section():

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

    section = 'Parameters'
    add = \
    """
    third : other_stuff
        Added description.
    """

    new_ds = docs_append_to_section(ds, section, add)

    assert 'third' in new_ds
    assert 'Added description' in new_ds
