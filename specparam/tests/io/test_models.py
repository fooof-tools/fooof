"""Tests for specparam.io.models.

Note: load tests load files created from save functions, so failures may reflect saving issues.
"""

import os

from specparam.core.items import OBJ_DESC
from specparam.io.files import load_json

from specparam.tests.tsettings import TEST_DATA_PATH

from specparam.io.models import *

###################################################################################################
###################################################################################################

def test_save_model_str(tfm):

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

    save_group(tft, file_name=res_file_name, file_path=TEST_DATA_PATH, save_results=True)
    save_group(tft, file_name=set_file_name, file_path=TEST_DATA_PATH, save_settings=True)
    save_group(tft, file_name=dat_file_name, file_path=TEST_DATA_PATH, save_data=True)

    assert os.path.exists(TEST_DATA_PATH / (res_file_name + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (set_file_name + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (dat_file_name + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_time_all'
    save_group(tft, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_event(tfe):

    res_file_name = 'test_event_res'
    set_file_name = 'test_event_set'
    dat_file_name = 'test_event_dat'

    save_event(tfe, file_name=res_file_name, file_path=TEST_DATA_PATH, save_results=True)
    save_event(tfe, file_name=set_file_name, file_path=TEST_DATA_PATH, save_settings=True)
    save_event(tfe, file_name=dat_file_name, file_path=TEST_DATA_PATH, save_data=True)

    assert os.path.exists(TEST_DATA_PATH / (set_file_name + '.json'))
    for ind in range(len(tfe)):
        assert os.path.exists(TEST_DATA_PATH / (res_file_name + '_' + str(ind) + '.json'))
        assert os.path.exists(TEST_DATA_PATH / (dat_file_name + '_' + str(ind) + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_event_all'
    save_event(tfe, file_name_all, TEST_DATA_PATH, False, True, True, True)
    for ind in range(len(tfe)):
        assert os.path.exists(TEST_DATA_PATH / (file_name_all + '_' + str(ind) + '.json'))

def test_load_model():

    # Loads file saved from `test_save_model_str`
    file_name = 'test_model_all'

    tmodel = load_model(file_name, TEST_DATA_PATH)
    assert tmodel

def test_load_group():

    # Loads file saved from `test_save_group`
    file_name = 'test_group_all'

    tgroup = load_group(file_name, TEST_DATA_PATH)
    assert tgroup

def test_load_time():

    # Loads file saved from `test_save_time`
    file_name = 'test_time_all'

    ttime = load_time(file_name, TEST_DATA_PATH)
    assert ttime

def test_load_event():

    # Loads file saved from `test_save_event`
    file_name = 'test_event_all'

    tevent = load_event(file_name, TEST_DATA_PATH)
    assert tevent

def test_load_file_contents():
    """Check that loaded model files contain the contents they should."""

    # Loads file saved from `test_save_model_str`
    file_name = 'test_model_all'

    loaded_data = load_json(file_name, TEST_DATA_PATH)

    for setting in OBJ_DESC['settings']:
        assert setting in loaded_data.keys()
    for result in OBJ_DESC['results']:
        assert result in loaded_data.keys()
    for datum in OBJ_DESC['data']:
        assert datum in loaded_data.keys()
