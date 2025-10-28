"""Tests for specparam.io.models.

Note: load tests load files created from save functions, so failures may reflect saving issues.
"""

import os

import numpy as np

from specparam import (SpectralModel, SpectralGroupModel,
                       SpectralTimeModel, SpectralTimeEventModel)
from specparam.models.utils import compare_model_objs
from specparam.io.files import load_json

from specparam.tests.tsettings import TEST_DATA_PATH

from specparam.io.models import *

###################################################################################################
###################################################################################################

def test_save_model(tfm):

    file_name_res = 'test_model_res'
    file_name_set = 'test_model_set'
    file_name_dat = 'test_model_dat'

    save_model(tfm, file_name_res, TEST_DATA_PATH, False, True, False, False)
    save_model(tfm, file_name_set, TEST_DATA_PATH, False, False, True, False)
    save_model(tfm, file_name_dat, TEST_DATA_PATH, False, False, False, True)

    assert os.path.exists(TEST_DATA_PATH / (file_name_res + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (file_name_set + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (file_name_dat + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_model_all'
    save_model(tfm, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_model2(tfm2):

    file_name_all = 'test_model_all2'
    save_model(tfm2, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_model_append(tfm):

    file_name = 'test_model_append'

    save_model(tfm, file_name, TEST_DATA_PATH, True, True, True, True)
    save_model(tfm, file_name, TEST_DATA_PATH, True, True, True, True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_model_fobj(tfm):

    file_name = 'test_model_fileobj'

    # Save, using file-object: three successive lines with three possible save settings
    with open(TEST_DATA_PATH / (file_name + '.json'), 'w') as f_obj:
        save_model(tfm, f_obj, TEST_DATA_PATH, False, True, False, False)
        save_model(tfm, f_obj, TEST_DATA_PATH, False, False, True, False)
        save_model(tfm, f_obj, TEST_DATA_PATH, False, False, False, True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_group(tfg):

    res_file_name = 'test_group_res'
    set_file_name = 'test_group_set'
    dat_file_name = 'test_group_dat'

    save_group(tfg, file_name=res_file_name, file_path=TEST_DATA_PATH, save_results=True)
    save_group(tfg, file_name=set_file_name, file_path=TEST_DATA_PATH, save_settings=True)
    save_group(tfg, file_name=dat_file_name, file_path=TEST_DATA_PATH, save_data=True)

    assert os.path.exists(TEST_DATA_PATH / (res_file_name + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (set_file_name + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (dat_file_name + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_group_all'
    save_group(tfg, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_group2(tfg2):

    file_name_all = 'test_group_all2'
    save_group(tfg2, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_group_append(tfg):

    file_name = 'test_group_append'

    save_group(tfg, file_name, TEST_DATA_PATH, True, save_results=True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_group_fobj(tfg):

    file_name = 'test_fileobj'

    with open(TEST_DATA_PATH / (file_name + '.json'), 'w') as f_obj:
        save_group(tfg, f_obj, TEST_DATA_PATH, False, True, False, False)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_time(tft):

    res_file_name = 'test_time_res'
    set_file_name = 'test_time_set'
    dat_file_name = 'test_time_dat'

    save_time(tft, file_name=res_file_name, file_path=TEST_DATA_PATH, save_results=True)
    save_time(tft, file_name=set_file_name, file_path=TEST_DATA_PATH, save_settings=True)
    save_time(tft, file_name=dat_file_name, file_path=TEST_DATA_PATH, save_data=True)

    assert os.path.exists(TEST_DATA_PATH / (res_file_name + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (set_file_name + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (dat_file_name + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_time_all'
    save_time(tft, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_event(tfe):

    res_file_name = 'test_event_res'
    set_file_name = 'test_event_set'
    dat_file_name = 'test_event_dat'

    save_event(tfe, file_name=res_file_name, file_path=TEST_DATA_PATH, save_results=True)
    save_event(tfe, file_name=set_file_name, file_path=TEST_DATA_PATH, save_settings=True)
    save_event(tfe, file_name=dat_file_name, file_path=TEST_DATA_PATH, save_data=True)

    assert os.path.exists(TEST_DATA_PATH / (set_file_name + '.json'))
    for ind in range(len(tfe.results)):
        assert os.path.exists(TEST_DATA_PATH / (res_file_name + '_' + str(ind) + '.json'))
        assert os.path.exists(TEST_DATA_PATH / (dat_file_name + '_' + str(ind) + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_event_all'
    save_event(tfe, file_name_all, TEST_DATA_PATH, False, True, True, True)
    for ind in range(len(tfe.results)):
        assert os.path.exists(TEST_DATA_PATH / (file_name_all + '_' + str(ind) + '.json'))

def test_load_file_contents(tfm):
    """Check that loaded model files contain the contents they should."""

    # Loads file saved from `test_save_model_str`
    loaded_data = load_json('test_model_all', TEST_DATA_PATH)

    for mode in tfm.modes.get_modes()._fields:
        assert mode in loaded_data.keys()

    assert 'bands' in loaded_data.keys()

    for setting in tfm.algorithm.settings.names:
        assert setting in loaded_data.keys()

    for rescomp in ['aperiodic', 'peak']:
        for version in ['fit', 'converted']:
            assert rescomp + '_' + version in loaded_data.keys()

    assert 'metrics' in loaded_data.keys()

    for datum in tfm.data._fields:
        assert datum in loaded_data.keys()

def test_load_model(tfm):

    # Loads file saved from `test_save_model_str`
    ntfm = load_model('test_model_all', TEST_DATA_PATH)

    assert isinstance(ntfm, SpectralModel)
    compare_model_objs([tfm, ntfm], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])

    for data in tfm.data._fields:
        assert np.array_equal(getattr(tfm.data, data), getattr(ntfm.data, data))

    for component in tfm.modes.components:
        assert not np.all(np.isnan(getattr(ntfm.results.params, component).get_params('fit')))
    assert tfm.results.metrics.results == ntfm.results.metrics.results

    # Check directory matches (loading didn't add any unexpected attributes)
    cfm = SpectralModel()
    assert dir(cfm) == dir(ntfm)
    assert dir(cfm.algorithm) == dir(ntfm.algorithm)
    assert dir(cfm.data) == dir(ntfm.data)
    assert dir(cfm.results) == dir(ntfm.results)
    assert dir(cfm.results.params) == dir(ntfm.results.params)

def test_load_model2(tfm2):

    # Loads file saved from `test_save_model_str2`
    ntfm2 = load_model('test_model_all2', TEST_DATA_PATH)
    compare_model_objs([tfm2, ntfm2], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])

def test_load_group(tfg):

    # Loads file saved from `test_save_group`
    ntfg = load_group('test_group_all', TEST_DATA_PATH)
    assert isinstance(ntfg, SpectralGroupModel)
    compare_model_objs([tfg, ntfg], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])
    for data in tfg.data._fields:
        assert np.array_equal(getattr(tfg.data, data), getattr(ntfg.data, data))
    assert len(ntfg.results.group_results) > 0
    for metric in tfg.results.metrics.labels:
        assert np.array_equal(tfg.results.get_metrics(metric), ntfg.results.get_metrics(metric))

    # Check directory matches (loading didn't add any unexpected attributes)
    cfg = SpectralGroupModel()
    assert dir(cfg) == dir(ntfg)
    assert dir(cfg.algorithm) == dir(ntfg.algorithm)
    assert dir(cfg.data) == dir(ntfg.data)
    assert dir(cfg.results) == dir(ntfg.results)
    assert dir(cfg.results.params) == dir(ntfg.results.params)

def test_load_group2(tfg2):

    # Loads file saved from `test_save_group_str2`
    ntfg2 = load_group('test_group_all2', TEST_DATA_PATH)
    compare_model_objs([tfg2, ntfg2], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])

def test_load_time(tft):

    # Loads file saved from `test_save_time`
    ntft = load_time('test_time_all', TEST_DATA_PATH)
    assert isinstance(tft, SpectralTimeModel)
    compare_model_objs([tft, ntft], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])
    for data in tft.data._fields:
        assert np.array_equal(getattr(tft.data, data), getattr(ntft.data, data))
    assert tft.results.time_results.keys() == ntft.results.time_results.keys()
    for key in tft.results.time_results:
        assert np.array_equal(\
            tft.results.time_results[key], ntft.results.time_results[key], equal_nan=True)

    # Check directory matches (loading didn't add any unexpected attributes)
    cft = SpectralTimeModel()
    assert dir(cft) == dir(ntft)
    assert dir(cft.algorithm) == dir(ntft.algorithm)
    assert dir(cft.data) == dir(ntft.data)
    assert dir(cft.results) == dir(ntft.results)
    assert dir(cft.results.params) == dir(ntft.results.params)

def test_load_event(tfe):

    # Loads file saved from `test_save_event`
    ntfe = load_event('test_event_all', TEST_DATA_PATH)
    assert isinstance(tfe, SpectralTimeEventModel)
    compare_model_objs([tfe, ntfe], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])
    for data in tfe.data._fields:
        assert np.array_equal(getattr(tfe.data, data), getattr(ntfe.data, data))
    assert len(tfe.results) > 1
    assert tfe.results.time_results.keys() == ntfe.results.time_results.keys()
    for key in tfe.results.time_results:
        assert np.array_equal(\
            tfe.results.time_results[key], ntfe.results.time_results[key], equal_nan=True)

    # Check directory matches (loading didn't add any unexpected attributes)
    cfe = SpectralTimeEventModel()
    assert dir(cfe) == dir(ntfe)
    assert dir(cfe.algorithm) == dir(ntfe.algorithm)
    assert dir(cfe.data) == dir(ntfe.data)
    assert dir(cfe.results) == dir(ntfe.results)
    assert dir(cfe.results.params) == dir(ntfe.results.params)
