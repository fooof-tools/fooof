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

def test_docs_drop_param(tdocstring):

    out = docs_drop_param(tdocstring)
    assert 'first' not in out
    assert 'second' in out

def test_docs_append_to_section(tdocstring):

    section = 'Parameters'
    add = \
    """
    third : other_stuff
        Added description.
    """

    new_ds = docs_append_to_section(tdocstring, section, add)

    assert 'third' in new_ds
    assert 'Added description' in new_ds

def test_get_docs_indices(tdocstring):

    inds = get_docs_indices(tdocstring)

    for el in DOCSTRING_SECTIONS:
        assert el in inds.keys()

    assert inds['Parameters'] == 2
    assert inds['Returns'] == 9

def test_docs_get_section(tdocstring):

    out1 = docs_get_section(tdocstring, 'Parameters', output='extract')
    assert 'Parameters' in out1
    assert 'Returns' not in out1

    out2 = docs_get_section(tdocstring, 'Parameters', output='remove')
    assert 'Parameters' not in out2
    assert 'Returns' in out2

def test_docs_add_section(tdocstring):

    tdocstring = tdocstring + \
    """\nNotes\n-----\n    % copied in at runtime"""

    new_section = \
    """Notes\n-----\n    \nThis is a new note."""
    new_docstring = docs_add_section(tdocstring, new_section)

    assert 'Notes' in new_docstring
    assert '%' not in new_docstring
    assert 'new note' in new_docstring
