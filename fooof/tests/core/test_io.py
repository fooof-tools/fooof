"""Tests for fooof.core.io."""

import os

from fooof.core.items import OBJ_DESC

from fooof.tests.settings import TEST_DATA_PATH

from fooof.core.io import *

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

def test_save_fm_str(tfm):
    """Check saving fm data, with file specifiers as strings."""

    # Test saving out each set of save elements
    file_name_res = 'test_fooof_res'
    file_name_set = 'test_fooof_set'
    file_name_dat = 'test_fooof_dat'

    save_fm(tfm, file_name_res, TEST_DATA_PATH, False, True, False, False)
    save_fm(tfm, file_name_set, TEST_DATA_PATH, False, False, True, False)
    save_fm(tfm, file_name_dat, TEST_DATA_PATH, False, False, False, True)

    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name_res + '.json'))
    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name_set + '.json'))
    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name_dat + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_fooof_all'
    save_fm(tfm, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name_all + '.json'))


def test_save_fm_append(tfm):
    """Check saving fm data, appending to a file."""

    file_name = 'test_fooof_append'

    save_fm(tfm, file_name, TEST_DATA_PATH, True, True, True, True)
    save_fm(tfm, file_name, TEST_DATA_PATH, True, True, True, True)

    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name + '.json'))

def test_save_fm_fobj(tfm):
    """Check saving fm data, with file object file specifier."""

    file_name = 'test_fooof_fileobj'

    # Save, using file-object: three successive lines with three possible save settings
    with open(os.path.join(TEST_DATA_PATH, file_name + '.json'), 'w') as f_obj:
        save_fm(tfm, f_obj, TEST_DATA_PATH, False, True, False, False)
        save_fm(tfm, f_obj, TEST_DATA_PATH, False, False, True, False)
        save_fm(tfm, f_obj, TEST_DATA_PATH, False, False, False, True)

    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name + '.json'))

def test_save_fg(tfg):
    """Check saving fg data."""

    res_file_name = 'test_fooofgroup_res'
    set_file_name = 'test_fooofgroup_set'
    dat_file_name = 'test_fooofgroup_dat'

    save_fg(tfg, file_name=res_file_name, file_path=TEST_DATA_PATH, save_results=True)
    save_fg(tfg, file_name=set_file_name, file_path=TEST_DATA_PATH, save_settings=True)
    save_fg(tfg, file_name=dat_file_name, file_path=TEST_DATA_PATH, save_data=True)

    assert os.path.exists(os.path.join(TEST_DATA_PATH, res_file_name + '.json'))
    assert os.path.exists(os.path.join(TEST_DATA_PATH, set_file_name + '.json'))
    assert os.path.exists(os.path.join(TEST_DATA_PATH, dat_file_name + '.json'))

    # Test saving out all save elements
    file_name_all = 'test_fooofgroup_all'
    save_fg(tfg, file_name_all, TEST_DATA_PATH, False, True, True, True)
    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name_all + '.json'))

def test_save_fg_append(tfg):
    """Check saving fg data, appending to file."""

    file_name = 'test_fooofgroup_append'

    save_fg(tfg, file_name, TEST_DATA_PATH, True, save_results=True)
    save_fg(tfg, file_name, TEST_DATA_PATH, True, save_results=True)

    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name + '.json'))

def test_save_fg_fobj(tfg):
    """Check saving fg data, with file object file specifier."""

    file_name = 'test_fooof_fileobj'

    with open(os.path.join(TEST_DATA_PATH, file_name + '.json'), 'w') as f_obj:
        save_fg(tfg, f_obj, TEST_DATA_PATH, False, True, False, False)

    assert os.path.exists(os.path.join(TEST_DATA_PATH, file_name + '.json'))

def test_load_json_str():
    """Test loading JSON file, with str file specifier.
    Loads files from test_save_fm_str.
    """

    file_name = 'test_fooof_all'

    data = load_json(file_name, TEST_DATA_PATH)

    assert data

def test_load_json_fobj():
    """Test loading JSON file, with file object file specifier.
    Loads files from test_save_fm_str.
    """

    file_name = 'test_fooof_all'

    with open(os.path.join(TEST_DATA_PATH, file_name + '.json'), 'r') as f_obj:
        data = load_json(f_obj, '')

    assert data

def test_load_jsonlines():
    """Test loading JSONlines file.
    Loads files from test_save_fg.
    """

    res_file_name = 'test_fooofgroup_res'

    for data in load_jsonlines(res_file_name, TEST_DATA_PATH):
        assert data

def test_load_file_contents():
    """Check that loaded files contain the contents they should.
    Note that is this test fails, it likely stems from an issue from saving.
    """

    file_name = 'test_fooof_all'
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
