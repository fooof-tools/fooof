"""Tests for specparam.io.files."""

from specparam.tests.settings import TEST_DATA_PATH

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
