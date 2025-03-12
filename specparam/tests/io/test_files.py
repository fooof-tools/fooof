"""Tests for specparam.io.files."""

from specparam.tests.tsettings import TEST_DATA_PATH

from specparam.io.files import *

###################################################################################################
###################################################################################################

def test_load_json_str():
    """Test loading JSON file, with str file specifier.
    Loads files from test_save_model_str.
    """

    file_name = 'test_model_all'

    data = load_json(file_name, TEST_DATA_PATH)

    assert data

def test_load_json_fobj():
    """Test loading JSON file, with file object file specifier.
    Loads files from test_save_model_str.
    """

    file_name = 'test_model_all'

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
    Note that if this test fails, it likely stems from an issue from saving.
    """

    file_name = 'test_model_all'
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
