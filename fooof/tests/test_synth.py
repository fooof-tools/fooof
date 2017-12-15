"""Test functions for FOOOF synth."""

from fooof.utils import mk_freq_vector
from fooof.synth import *

###################################################################################################
###################################################################################################

def test_mk_fake_data():

    xs = mk_freq_vector([3, 50], 0.5)

    bgp = [50, 2]
    oscs = [[10, 0.5, 2],
            [20, 0.3, 4]]

    xs, ys = mk_fake_data(xs, bgp, [it for osc in oscs for it in osc])

    assert np.all(xs)
    assert np.all(ys)
    assert len(xs) == len(ys)

def test_mk_fake_group_data():

    xs = mk_freq_vector([3, 50], 0.5)

    xs, ys = mk_fake_group_data(xs)

    assert np.all(xs)
    assert np.all(ys)
    assert ys.ndim == 2
