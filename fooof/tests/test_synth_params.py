"""   """

from fooof.synth.params import *

###################################################################################################
###################################################################################################

def test_stepper():

    assert Stepper(8,12,.1)

    # TODO: add more tests of Stepper

def test_param_iter():

    # Test oscillations
    step = Stepper(8, 12, .1)
    osc = [step, .5, .5]
    iter_1 = param_iter(osc)

    for ind, val in enumerate(iter_1):
        assert val == [8 + (.1*ind), .5 , .5]

    # Test aperiodic
    step = Stepper(.25, 3, .25)
    bg = [0, step]
    iter_1 = param_iter(bg)

    for ind, val in enumerate(iter_1):
        assert val == [0, .25 + (.25*ind)]

    # Test n oscillations
    step = Stepper(8, 12, .1)
    oscs = [step, .5, .5, 10, .25, 1]
    iter_1 = param_iter(oscs)

    for ind, val in enumerate(iter_1):
        assert val == [8 + (.1*ind), .5 , .5, 10, .25, 1]

    # Test list of lists
    step = Stepper(8, 12, .1)
    osc_1 = [1, 2, 3]
    osc_2 = [4, 5, 6]
    osc_3 = [7, 8, step]
    oscs = [osc_1, osc_2, osc_3]
    iter_2 = param_iter(oscs)

    for ind, val in enumerate(iter_2):
        assert val == [1, 2, 3, 4, 5, 6, 7, 8, 8 + (.1*ind)]

def test_param_sampler():

    pos = [1, 2, 3, 4]
    gen = param_sampler(pos)

    for ind, el in zip(range(3), gen):
        assert el in pos
