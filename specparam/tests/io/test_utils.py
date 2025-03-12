"""Tests for specparam.io.utils"""

from pathlib import Path

from specparam.io.utils import *

###################################################################################################
###################################################################################################

def test_fname():
    """Check that the file name checker helper function properly checks / adds file extensions."""

    assert fname('data', 'json') == 'data.json'
    assert fname('data.json', 'json') == 'data.json'
    assert fname('pic', 'png') == 'pic.png'
    assert fname('pic.png', 'png') == 'pic.png'
    assert fname('report.pdf', 'pdf') == 'report.pdf'
    assert fname('report.png', 'pdf') == 'report.png'

def test_fpath():
    """Check that the file path checker helper function properly checks / combines file paths."""

    assert fpath(None, 'data.json') == 'data.json'
    assert fpath('/path/', 'data.json') == '/path/data.json'
    assert fpath(Path('/path/'), 'data.json') == '/path/data.json'

def test_get_files():

    out1 = get_files('.')
    assert isinstance(out1, list)

    out2 = get_files('.', 'search')
    assert isinstance(out2, list)
