"""Test functions for specparam.models.utils."""

from pytest import raises

import numpy as np

from specparam import SpectralGroupModel
from specparam.sim import sim_group_power_spectra
from specparam.metrics.definitions import METRICS
from specparam.modutils.errors import NoModelError, IncompatibleSettingsError

from specparam.tests.tdata import default_group_params

from specparam.models.utils import *

###################################################################################################
###################################################################################################

def test_initialize_model_from_source(tfm, tfg):

    for source in [tfm, tfg]:
        for target in ['model', 'group', 'time', 'event']:
            out = initialize_model_from_source(source, target)
            assert out.algorithm.get_settings() == source.algorithm.get_settings()
            assert out.data.get_meta_data() == source.data.get_meta_data()
            assert out.modes.get_modes() == source.modes.get_modes()
            assert not out.data.has_data
            assert not out.results.has_model

def test_compare_model_objs(tfm, tfg):

    for f_obj in [tfm, tfg]:

        f_obj2 = f_obj.copy()

        assert compare_model_objs([f_obj, f_obj2],
                                  ['modes', 'settings', 'meta_data', 'bands', 'metrics'])

        assert compare_model_objs([f_obj, f_obj2], 'modes')
        f_obj2.add_modes('knee', 'cauchy')
        assert not compare_model_objs([f_obj, f_obj2], 'modes')

        assert compare_model_objs([f_obj, f_obj2], 'settings')
        f_obj2.algorithm.settings.peak_width_limits = [2, 4]
        assert not compare_model_objs([f_obj, f_obj2], 'settings')

        assert compare_model_objs([f_obj, f_obj2], 'meta_data')
        f_obj2.data.freq_range = [5, 25]
        assert not compare_model_objs([f_obj, f_obj2], 'meta_data')

        assert compare_model_objs([f_obj, f_obj2], 'bands')
        f_obj2.results.add_bands({'new' : [1, 4]})
        assert not compare_model_objs([f_obj, f_obj2], 'bands')

        assert compare_model_objs([f_obj, f_obj2], 'metrics')
        f_obj2.results.metrics.add_metric(METRICS['error_rmse'])
        assert not compare_model_objs([f_obj, f_obj2], 'metrics')

def test_average_group(tfg, tbands):

    nfm = average_group(tfg, tbands)
    assert nfm

    # Test bad average method error
    with raises(ValueError):
        average_group(tfg, tbands, avg_method='BAD')

    # Test no data available error
    ntfg = SpectralGroupModel()
    with raises(NoModelError):
        average_group(ntfg, tbands)

def test_average_reconstructions(tfg):

    freqs, avg_model = average_reconstructions(tfg)
    assert isinstance(freqs, np.ndarray)
    assert isinstance(avg_model, np.ndarray)
    assert freqs.shape == avg_model.shape

def test_combine_model_objs(tfm, tfg):

    tfm2 = tfm.copy()
    tfm3 = tfm.copy()
    tfg2 = tfg.copy()
    tfg3 = tfg.copy()

    # Check combining 2 model objects
    nfg1 = combine_model_objs([tfm, tfm2])
    assert nfg1
    assert len(nfg1.results) == 2
    assert compare_model_objs([nfg1, tfm], 'settings')
    assert nfg1.results.group_results[0] == tfm.results.get_results()
    assert nfg1.results.group_results[-1] == tfm2.results.get_results()

    # Check combining 3 model objects
    nfg2 = combine_model_objs([tfm, tfm2, tfm3])
    assert nfg2
    assert len(nfg2.results) == 3
    assert compare_model_objs([nfg2, tfm], 'settings')
    assert nfg2.results.group_results[0] == tfm.results.get_results()
    assert nfg2.results.group_results[-1] == tfm3.results.get_results()

    # Check combining 2 group objects
    nfg3 = combine_model_objs([tfg, tfg2])
    assert nfg3
    assert len(nfg3.results) == len(tfg.results) + len(tfg2.results)
    assert compare_model_objs([nfg3, tfg, tfg2], 'settings')
    assert nfg3.results.group_results[0] == tfg.results.group_results[0]
    assert nfg3.results.group_results[-1] == tfg2.results.group_results[-1]

    # Check combining 3 group objects
    nfg4 = combine_model_objs([tfg, tfg2, tfg3])
    assert nfg4
    assert len(nfg4.results) == len(tfg.results) + len(tfg2.results) + len(tfg3.results)
    assert compare_model_objs([nfg4, tfg, tfg2, tfg3], 'settings')
    assert nfg4.results.group_results[0] == tfg.results.group_results[0]
    assert nfg4.results.group_results[-1] == tfg3.results.group_results[-1]

    # Check combining a mixture of model & group objects
    nfg5 = combine_model_objs([tfg, tfm, tfg2, tfm2])
    assert nfg5
    assert len(nfg5.results) == len(tfg.results) + 1 + len(tfg2.results) + 1
    assert compare_model_objs([nfg5, tfg, tfm, tfg2, tfm2], 'settings')
    assert nfg5.results.group_results[0] == tfg.results.group_results[0]
    assert nfg5.results.group_results[-1] == tfm2.results.get_results()

    # Check combining objects with no data
    tfm2._reset_data_results(False, True, True)
    tfg2._reset_data_results(False, True, True, True)
    nfg6 = combine_model_objs([tfm2, tfg2])
    assert len(nfg6.results) == 1 + len(tfg2.results)
    assert nfg6.data.power_spectra is None

def test_combine_errors(tfm, tfg):

    # Incompatible settings
    for f_obj in [tfm, tfg]:
        f_obj2 = f_obj.copy()
        f_obj2.algorithm.settings.peak_width_limits = [2, 4]
        with raises(IncompatibleSettingsError):
            combine_model_objs([f_obj, f_obj2])

    # Incompatible data information
    for f_obj in [tfm, tfg]:
        f_obj2 = f_obj.copy()
        f_obj2.data.freq_range = [5, 30]

        with raises(IncompatibleSettingsError):
            combine_model_objs([f_obj, f_obj2])

def test_fit_models_3d(tfg):

    n_groups = 2
    n_spectra = 3
    xs, ys = sim_group_power_spectra(n_spectra, *default_group_params())
    ys = np.stack([ys] * n_groups, axis=0)
    spectra_shape = np.shape(ys)

    tfg = SpectralGroupModel()
    fgs = fit_models_3d(tfg, xs, ys)

    assert len(fgs) == n_groups == spectra_shape[0]
    for fg in fgs:
        assert fg
        assert len(fg.results) == n_spectra
        assert fg.data.power_spectra.shape == spectra_shape[1:]
