"""Utilities for testing fooof."""

from fooof import FOOOF, FOOOFGroup
from fooof.synth import mk_fake_data, mk_fake_group_data
from fooof.utils import mk_freq_vector

###################################################################################################
###################################################################################################

def get_fm():
    """Get a FOOOF object, with a fit PSD, for testing."""

    xs, ys = mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4])

    fm = FOOOF()
    fm.fit(xs, ys)

    return fm

def get_fg():
    """Get a FOOOFGroup object, with some fit PSDs, for testing."""

    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), 2)

    fg = FOOOFGroup()
    fg.fit(xs, ys)

    return fg
