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
    file_name = 'test_model_all'

    loaded_data = load_json(file_name, TEST_DATA_PATH)

    for mode in tfm.modes.get_modes()._fields:
        assert mode in loaded_data.keys()
    assert 'bands' in loaded_data.keys()
    for setting in tfm.algorithm.settings.names:
        assert setting in loaded_data.keys()
    for result in tfm.results._fields:
        assert result in loaded_data.keys()
    assert 'metrics' in loaded_data.keys()
    for datum in tfm.data._fields:
        assert datum in loaded_data.keys()

def test_load_model(tfm):

    # Loads file saved from `test_save_model_str`
    file_name = 'test_model_all'
    ntfm = load_model(file_name, TEST_DATA_PATH)
    assert isinstance(ntfm, SpectralModel)

    # Check that all elements get loaded
    assert tfm.modes.get_modes() == ntfm.modes.get_modes()
    assert tfm.results.bands == ntfm.results.bands
    for meta_dat in tfm.data._meta_fields:
        assert getattr(ntfm.data, meta_dat) is not None
    for setting in ntfm.algorithm.settings.names:
        assert getattr(ntfm.algorithm, setting) is not None
    for result in tfm.results._fields:
        assert not np.all(np.isnan(getattr(ntfm.results, result)))
    assert tfm.results.metrics.results == ntfm.results.metrics.results
    for data in tfm.data._fields:
        assert getattr(ntfm.data, data) is not None

    # Check directory matches (loading didn't add any unexpected attributes)
    cfm = SpectralModel()
    assert dir(cfm) == dir(ntfm)
    assert dir(cfm.data) == dir(ntfm.data)
    assert dir(cfm.results) == dir(ntfm.results)

def test_load_model2(tfm2):

    # Loads file saved from `test_save_model_str2`
    file_name = 'test_model_all2'
    ntfm2 = load_model(file_name, TEST_DATA_PATH)
    assert tfm2.modes.get_modes() == ntfm2.modes.get_modes()
    compare_model_objs([tfm2, ntfm2], ['settings', 'meta_data', 'metrics'])

def test_load_group(tfg):

    # Loads file saved from `test_save_group`
    file_name = 'test_group_all'
    ntfg = load_group(file_name, TEST_DATA_PATH)
    assert isinstance(ntfg, SpectralGroupModel)

    # Check that all elements get loaded
    assert tfg.modes.get_modes() == ntfg.modes.get_modes()
    assert tfg.results.bands == ntfg.results.bands
    for setting in tfg.algorithm.settings.names:
        assert getattr(ntfg.algorithm, setting) is not None
    assert len(ntfg.results.group_results) > 0
    for metric in tfg.results.metrics.labels:
        assert tfg.results.metrics.results[metric] is not None
    assert ntfg.data.power_spectra is not None
    for meta_dat in tfg.data._meta_fields:
        assert getattr(ntfg.data, meta_dat) is not None

    # Check directory matches (loading didn't add any unexpected attributes)
    cfg = SpectralGroupModel()
    assert dir(cfg) == dir(ntfg)
    assert dir(cfg.data) == dir(ntfg.data)
    assert dir(cfg.results) == dir(ntfg.results)

def test_load_group2(tfg2):

    # Loads file saved from `test_save_group_str2`
    file_name = 'test_group_all2'
    ntfg2 = load_group(file_name, TEST_DATA_PATH)
    assert tfg2.modes.get_modes() == ntfg2.modes.get_modes()
    compare_model_objs([tfg2, ntfg2], ['settings', 'meta_data', 'metrics'])

def test_load_time():

    # Loads file saved from `test_save_time`
    file_name = 'test_time_all'

    # Load without bands definition
    tft = load_time(file_name, TEST_DATA_PATH)
    assert isinstance(tft, SpectralTimeModel)
    assert tft.results.time_results

    # Check directory matches (loading didn't add any unexpected attributes)
    cft = SpectralTimeModel()
    assert dir(cft) == dir(tft)
    assert dir(cft.data) == dir(tft.data)
    assert dir(cft.results) == dir(tft.results)

def test_load_event():

    # Loads file saved from `test_save_event`
    file_name = 'test_event_all'

    # Load without bands definition
    tfe = load_event(file_name, TEST_DATA_PATH)
    assert isinstance(tfe, SpectralTimeEventModel)
    assert len(tfe.results) > 1
    assert tfe.results.event_time_results

    # Check directory matches (loading didn't add any unexpected attributes)
    cfe = SpectralTimeEventModel()
    assert dir(cfe) == dir(tfe)
    assert dir(cfe.data) == dir(tfe.data)
    assert dir(cfe.results) == dir(tfe.results)
