"""Tests for specparam.modutils.functions."""

from specparam.modutils.functions import *

###################################################################################################
###################################################################################################

def test_resolve_aliases():

    # Define a test set of aliases
    aliases = {'linewidth' : ['lw', 'linewidth'],
               'markersize' : ['ms', 'markersize']}

    # Test resolving aliases with aliased value present, that should change
    kwargs1 = {'alpha' : 0.7, 'lw' : 2}
    assert resolve_aliases(kwargs1, aliases) == {'alpha' : 0.7, 'linewidth' : 2}

    # Test resolving aliases with aliased value present, that should stay the same
    kwargs2 = {'alpha' : 0.7, 'linewidth' : 2}
    assert resolve_aliases(kwargs2, aliases) == {'alpha' : 0.7, 'linewidth' : 2}

    # Test resolving aliases with multiple values to be aliased
    kwargs3 = {'lw' : 2.0, 'ms' : 12, 'ot' : 1}
    assert resolve_aliases(kwargs3, aliases) == {'linewidth' : 2.0, 'markersize' : 12, 'ot' : 1}

    # Test resolving aliases with no aliased values present
    kwargs4 = {'alpha' : 10, 'beta' : 20}
    assert resolve_aliases(kwargs4, aliases) == {'alpha' : 10, 'beta' : 20}
