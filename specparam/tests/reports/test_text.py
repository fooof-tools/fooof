"""Tests for specparam.reports.text."""

from specparam.reports.text import *

###################################################################################################
###################################################################################################

def test_gen_methods_text(tfm):

    # Test with and without passing in a model object
    assert gen_methods_text()
    assert gen_methods_text(tfm)
