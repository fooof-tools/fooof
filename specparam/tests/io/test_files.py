"""Tests for specparam.io.files.

Note: load tests load files created from save functions, so failures may reflect saving issues.
"""

import os

from specparam.tests.tsettings import TEST_DATA_PATH

from specparam.io.files import *

###################################################################################################
###################################################################################################

def test_save_json_str():

    data = {'a' : 1, 'b' : 2}
    file_name = 'test_json_str'
    save_json(data, file_name, TEST_DATA_PATH)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_json_str_append():

    data1 = {'a' : 1, 'b' : 2}
    data2 = {'a' : 3, 'b' : 4}
    file_name = 'test_json_str_app'
    save_json(data1, file_name, TEST_DATA_PATH)
    save_json(data2, file_name, TEST_DATA_PATH, append=True)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_save_json_fobj():

    data = {'a' : 1, 'b' : 2}
    file_name = 'test_json_fobj'
    with open(TEST_DATA_PATH / (file_name + '.json'), 'w') as f_obj:
        save_json(data, f_obj, TEST_DATA_PATH)

    assert os.path.exists(TEST_DATA_PATH / (file_name + '.json'))

def test_load_json_str():

    # Loads file saved from `test_save_json_str`
    file_name = 'test_json_str'

    data = load_json(file_name, TEST_DATA_PATH)

    assert data

def test_load_json_fobj():

    # Loads file saved from `test_save_json_str`
    file_name = 'test_json_str'

    with open(TEST_DATA_PATH / (file_name + '.json'), 'r') as f_obj:
        data = load_json(f_obj, '')

    assert data

def test_load_jsonlines():

    # Loads file saved from `test_save_json_str_append`
    res_file_name = 'test_json_str_app'

    for data in load_jsonlines(res_file_name, TEST_DATA_PATH):
        assert data
