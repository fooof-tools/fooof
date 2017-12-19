"""Utilities for testing fooof."""

from fooof import FOOOF, FOOOFGroup
from fooof.synth import mk_fake_data, mk_fake_group_data
from fooof.utils import mk_freq_vector
from fooof.core.modutils import safe_import

###################################################################################################
###################################################################################################

def get_tfm():
    """Get a FOOOF object, with a fit PSD, for testing."""

    xs, ys = mk_fake_data(mk_freq_vector([3, 50], 0.5), [50, 2], [10, 0.5, 2, 20, 0.3, 4])

    tfm = FOOOF()
    tfm.fit(xs, ys)

    return tfm

def get_tfg():
    """Get a FOOOFGroup object, with some fit PSDs, for testing."""

    xs, ys = mk_fake_group_data(mk_freq_vector([3, 50], 0.5), 2)

    tfg = FOOOFGroup()
    tfg.fit(xs, ys)

    return tfg

# def check_mpl():
#     """   """

#     if safe_import('matplotlib'):
#         return True
#     else:
#         return False
