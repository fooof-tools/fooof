"""Tests for specparam.core.io."""

import os
from pathlib import Path

from specparam.core.items import OBJ_DESC

from specparam.tests.settings import TEST_DATA_PATH

from specparam.core.io import *

###################################################################################################
###################################################################################################

def test_fname():
    """Check that the file name checker helper function properly checks / adds file extensions."""

    assert fname('data', 'json') == 'data.json'
    assert fname('data.json', 'json') == 'data.json'
    assert fname('pic', 'png') == 'pic.png'
    assert fname('pic.png', 'png') == 'pic.png'
    assert fname('report.pdf', 'pdf') == 'report.pdf'
    assert fname('report.png', 'pdf') == 'report.png'

def test_fpath():
    """Check that the file path checker helper function properly checks / combines file paths."""

    assert fpath(None, 'data.json') == 'data.json'
    assert fpath('/path/', 'data.json') == '/path/data.json'
    assert fpath(Path('/path/'), 'data.json') == '/path/data.json'

def test_get_files():

    out1 = get_files('.')
    assert isinstance(out1, list)

    out2 = get_files('.', 'search')
    assert isinstance(out2, list)

def test_save_model_str(tfm):
    """Check saving model object data, with file specifiers as strings."""

    # Test saving out each set of save elements
    file_name_res = 'test_res'
    file_name_set = 'test_set'
    file_name_dat = 'test_dat'

    save_model(tfm, file_name_res, TEST_DATA_PATH, False, True, False, False)
    save_model(tfm, file_name_set, TEST_DATA_PATH, False, False, True, False)
    save_model(tfm, file_name_dat, TEST_DATA_PATH, False, False, False, True)

    assert os.path.exists(TEST_DATA_PATH / (file_name_res + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (file_name_set + '.json'))
    assert os.path.exists(TEST_DATA_PATH / (file_name_dat + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_all'
    save_model(tfm, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(TEST_DATA_PATH / (file_name_all + '.json'))

def test_save_model_append(tfm):
    """Check saving fm data, appending to a file."""

    file_name = 'test_append'

    save_model(tfm, file_name, TEST_DATA_PATH, True, True, True, True)
    save_model(tfm, file_name, TEST_DATA_PATH, True, True, True, True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_model_fobj(tfm):
    """Check saving fm data, with file object file specifier."""

    file_name = 'test_fileobj'

    # Save, using file-object: three successive lines with three possible save settings
    with open(TEST_DATA_PATH / (file_name + '.json'), 'w') as f_obj:
        save_model(tfm, f_obj, TEST_DATA_PATH, False, True, False, False)
        save_model(tfm, f_obj, TEST_DATA_PATH, False, False, True, False)
        save_model(tfm, f_obj, TEST_DATA_PATH, False, False, False, True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_group(tfg):
    """Check saving fg data."""

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
    """Check saving fg data, appending to file."""

    file_name = 'test_group_append'

    save_group(tfg, file_name, TEST_DATA_PATH, True, save_results=True)
    save_group(tfg, file_name, TEST_DATA_PATH, True, save_results=True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_group_fobj(tfg):
    """Check saving fg data, with file object file specifier."""

    file_name = 'test_fileobj'

    with open(TEST_DATA_PATH / (file_name + '.json'), 'w') as f_obj:
        save_group(tfg, f_obj, TEST_DATA_PATH, False, True, False, False)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_time(tft):
    """Check saving ft data."""

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
    """Check saving fe data."""

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

def test_load_json_str():
    """Test loading JSON file, with str file specifier.
    Loads files from test_save_model_str.
    """

    file_name = 'test_all'

    data = load_json(file_name, TEST_DATA_PATH)

    assert data

def test_load_json_fobj():
    """Test loading JSON file, with file object file specifier.
    Loads files from test_save_model_str.
    """

    file_name = 'test_all'

    with open(TEST_DATA_PATH / (file_name + '.json'), 'r') as f_obj:
        data = load_json(f_obj, '')

    assert data

def test_load_jsonlines():
    """Test loading JSONlines file.
    Loads files from test_save_group.
    """

    res_file_name = 'test_group_res'

    for data in load_jsonlines(res_file_name, TEST_DATA_PATH):
        assert data

def test_load_file_contents():
    """Check that loaded files contain the contents they should.
    Note that is this test fails, it likely stems from an issue from saving.
    """

    file_name = 'test_all'
    loaded_data = load_json(file_name, TEST_DATA_PATH)

    # Check settings
    for setting in OBJ_DESC['settings']:
        assert setting in loaded_data.keys()

    # Check results
    for result in OBJ_DESC['results']:
        assert result in loaded_data.keys()

    # Check results
    for datum in OBJ_DESC['data']:
        assert datum in loaded_data.keys()
