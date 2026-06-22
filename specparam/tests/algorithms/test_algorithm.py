"""Tests for specparam.algorthms.algorithm."""

from specparam.modes.modes import Modes
from specparam.algorithms.settings import SettingsDefinition

from specparam.algorithms.algorithm import *

###################################################################################################
###################################################################################################

def test_algorithm():

    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    algo = Algorithm(public_settings=tsettings)
    assert algo
    assert isinstance(algo.public_settings, SettingsDefinition)
    assert algo.public_settings == tsettings
    for setting in algo.public_settings.names:
        assert getattr(algo.settings, setting) is None
    algo.print()

def test_algorithm_settings():

    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    talgo = Algorithm(public_settings=tsettings)

    model_settings = talgo.public_settings.make_model_settings()
    settings = model_settings(a=1, b=2)
    talgo.add_settings(settings)
    for setting in settings._fields:
        assert getattr(talgo.settings, setting) == getattr(settings, setting)

    settings_out = talgo.get_settings()
    assert isinstance(settings, model_settings)
    assert settings_out == settings

def test_algorithm_cf():

    tsettings = SettingsDefinition({
        'a' : {'type' : 'a type desc', 'description' : 'a desc'},
        'b' : {'type' : 'b type desc', 'description' : 'b desc'},
    })

    algo = AlgorithmCF(public_settings=tsettings)

    assert isinstance(algo._cf_settings_desc, SettingsDefinition)
    assert algo._cf_settings
    for setting in algo._cf_settings.names:
        assert getattr(algo._cf_settings, setting) is None

def test_algorithm_cf_initialize():

    algo = AlgorithmCF(public_settings={'a' : {'type' : 'a type desc', 'description' : 'a desc'}},
                       modes=Modes('fixed', 'gaussian'))

    ap_bounds = algo._initialize_bounds('aperiodic')
    assert len(ap_bounds[0]) == algo.modes.aperiodic.n_params
    pe_bounds = algo._initialize_bounds('periodic')
    assert len(pe_bounds[0]) == algo.modes.periodic.n_params

    ap_guess = algo._initialize_guess('aperiodic')
    assert len(ap_guess) == algo.modes.aperiodic.n_params
    pe_guess = algo._initialize_guess('periodic')
    assert len(pe_guess) == algo.modes.periodic.n_params
