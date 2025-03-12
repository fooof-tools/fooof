"""Tests for specparam.modutils.docs.

Note: the decorators for copying documentation are not currently tested.
"""

from specparam.modutils.docs import *

###################################################################################################
###################################################################################################

def test_docs_drop_param(tdocstring):

    out = docs_drop_param(tdocstring)
    assert 'first' not in out
    assert 'second' in out

def test_docs_replace_param(tdocstring):

    new_param = 'updated : other\n        This description has been dropped in.'

    ndocstring1 = docs_replace_param(tdocstring, 'first', new_param)
    assert 'updated' in ndocstring1
    assert 'first' not in ndocstring1
    assert 'second' in ndocstring1

    ndocstring2 = docs_replace_param(tdocstring, 'second', new_param)
    assert 'updated' in ndocstring2
    assert 'first' in ndocstring2
    assert 'second' not in ndocstring2

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

    # Test with end_selection
    out3 = docs_get_section(tdocstring, 'Parameters', output='extract', end='Returns')
    assert 'Parameters' in out3
    assert 'Returns' not in out3

def test_docs_add_section(tdocstring):

    tdocstring = tdocstring + \
    """\nNotes\n-----\n    % copied in"""

    new_section = \
    """Notes\n-----\n    \nThis is a new note."""
    new_docstring = docs_add_section(tdocstring, new_section)

    assert 'Notes' in new_docstring
    assert '%' not in new_docstring
    assert 'new note' in new_docstring

def test_copy_doc_func_to_method(tdocstring):

    def tfunc(): pass
    tfunc.__doc__ = tdocstring

    class tobj():

        @copy_doc_func_to_method(tfunc)
        def tmethod():
            pass

    assert tobj.tmethod.__doc__
    assert 'first' not in tobj.tmethod.__doc__
    assert 'second' in tobj.tmethod.__doc__


def test_copy_doc_class(tdocstring):

    class tobj1():
        pass
    tobj1.__doc__ = tdocstring

    new_section = \
    """
    third : stuff
        Words, words, words.
    """
    @copy_doc_class(tobj1, 'Parameters', new_section)
    class tobj2():
        pass

    assert 'third' in tobj2.__doc__
    assert 'third' not in tobj1.__doc__

def test_replace_docstring_sections(tdocstring):

    # Extract just the parameters section from general test docstring
    new_parameters = '\n'.join(tdocstring.split('\n')[2:8])

    @replace_docstring_sections(new_parameters)
    def tfunc():
        """Test function docstring

        Parameters
        ----------
        % copied in
        """
        pass

    assert 'first' in tfunc.__doc__
    assert 'second' in tfunc.__doc__
