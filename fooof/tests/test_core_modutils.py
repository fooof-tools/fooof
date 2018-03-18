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

def test_get_data_indices():

    indices_fixed = get_data_indices('fixed')
    assert indices_fixed
    for ke, va in indices_fixed.items():
        if ke == 'knee':
            assert not va
        else:
            assert isinstance(va, int)

    indices_knee = get_data_indices('knee')
    assert indices_knee
    for ke, va in indices_knee.items():
        assert isinstance(va, int)

def test_docs_drop_param():

    ds = """STUFF

    Parameters
    ----------
    first : thing
        Words, words, words.
    second : stuff
        Words, words, words.

    Returns
    -------
    out : yay
        Words, words, words.
    """

    out = docs_drop_param(ds)
    assert 'first' not in out
    assert 'second' in out

def test_docs_append_to_section():

    ds = """STUFF

    Parameters
    ----------
    first : thing
        Words, words, words.
    second : stuff
        Words, words, words.

    Returns
    -------
    out : yay
        Words, words, words.
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
