"""Tests for fooof.core.modutils.

Note: the decorators for copying documentation are not currently tested.
"""

from pytest import raises

from fooof.core.modutils import *

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
