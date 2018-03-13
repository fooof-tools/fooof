"""Tests for fooof.core.io."""

import os
import pkg_resources as pkg

from fooof import FOOOF
from fooof.core.modutils import get_obj_desc

from fooof.core.io import *
from fooof.core.io import _check_fname

###################################################################################################
###################################################################################################

def test_save_fm_str(tfm):
    """Check saving fm data, with str file specifier."""

    file_name_all = 'test_fooof_str_all'
    file_name_res = 'test_fooof_str_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    save_fm(tfm, file_name_all, file_path, False, True, True, True)
    save_fm(tfm, file_name_res, file_path, False, True, False, False)

    assert os.path.exists(os.path.join(file_path, file_name_all + '.json'))
    assert os.path.exists(os.path.join(file_path, file_name_res + '.json'))

def test_save_fm_str_app(tfm):
    """Check saving fm data, with str file specifier, with appending."""

    file_name = 'test_fooof_str_app'
    file_path = pkg.resource_filename(__name__, 'test_files')

    save_fm(tfm, file_name, file_path, True, True, True, True)
    save_fm(tfm, file_name, file_path, True, True, True, True)

    assert os.path.exists(os.path.join(file_path, file_name + '.json'))

def test_save_fm_fobj(tfm):
    """Check saving fm data, with file object file specifier."""

    file_name = 'test_fooof_fobj'
    file_path = pkg.resource_filename(__name__, 'test_files')

    # Save, using file-object: three successive lines with three possible save settings
    with open(os.path.join(file_path, file_name + '.json'), 'w') as f_obj:
        save_fm(tfm, f_obj, file_path, False, True, False, False)
        save_fm(tfm, f_obj, file_path, False, False, True, False)
        save_fm(tfm, f_obj, file_path, False, False, False, True)

    assert os.path.exists(os.path.join(file_path, file_name + '.json'))

def test_save_fg(tfg):
    """Check saving fg data."""

    set_file_name = 'test_fooof_group_set'
    res_file_name = 'test_fooof_group_res'
    dat_file_name = 'test_fooof_group_dat'
    file_path = pkg.resource_filename(__name__, 'test_files')

    save_fg(tfg, file_name=set_file_name, file_path=file_path, save_settings=True)
    save_fg(tfg, file_name=res_file_name, file_path=file_path, save_results=True)
    save_fg(tfg, file_name=dat_file_name, file_path=file_path, save_data=True)

    assert os.path.exists(os.path.join(file_path, set_file_name + '.json'))
    assert os.path.exists(os.path.join(file_path, res_file_name + '.json'))
    assert os.path.exists(os.path.join(file_path, dat_file_name + '.json'))

def test_save_fg_app(tfg):
    """Check saving fg data, appending to file."""

    file_name = 'test_fooof_group_str_app'
    file_path = pkg.resource_filename(__name__, 'test_files')

    save_fg(tfg, file_name, file_path, True, save_results=True)
    save_fg(tfg, file_name, file_path, True, save_results=True)

    assert os.path.exists(os.path.join(file_path, file_name + '.json'))

def test_save_fg_fobj(tfg):
    """Check saving fg data, with file object file specifier."""

    file_name = 'test_fooof_fobj'
    file_path = pkg.resource_filename(__name__, 'test_files')

    with open(os.path.join(file_path, file_name + '.json'), 'w') as f_obj:
        save_fg(tfg, f_obj, file_path, False, True, False, False)

    assert os.path.exists(os.path.join(file_path, file_name + '.json'))

def test_load_json_str():
    """Test loading JSON file, with str file specifier. Loads files from test_save_fm_str."""

    file_name = 'test_fooof_str_all'
    file_path = pkg.resource_filename(__name__, 'test_files')

    dat = load_json(file_name, file_path)

    assert dat

def test_load_json_fobj():
    """Test loading JSON file, with file object file specifier. Loads files from test_save_fm_str."""

    file_name = 'test_fooof_str_all'
    file_path = pkg.resource_filename(__name__, 'test_files')

    with open(os.path.join(file_path, file_name + '.json'), 'r') as f_obj:
        dat = load_json(f_obj, '')

    assert dat

def test_load_jsonlines():
    """Test loading JSONlines file. Loads files from test_save_fg."""

    res_file_name = 'test_fooof_group_res'
    file_path = pkg.resource_filename(__name__, 'test_files')

    for dat in load_jsonlines(res_file_name, file_path):
        assert dat

def test_load_file_contents():
    """Check that loaded files contain the contents they should.

    Note that is this test fails, it likely stems from an issue from saving.
    """

    file_name = 'test_fooof_str_all'
    file_path = pkg.resource_filename(__name__, 'test_files')

    loaded_data = load_json(file_name, file_path)

    desc = get_obj_desc()

    # Check settings
    for setting in desc['settings']:
        assert setting in loaded_data.keys()

    # Check results
    for result in desc['results']:
        assert result in loaded_data.keys()

    # Check results
    for datum in desc['data']:
        assert datum in loaded_data.keys()

def test_check_fname():
    """Check that the file name checker helper function properly checks / adds file extensions."""

    assert _check_fname('dat') == 'dat.json'
    assert _check_fname('dat.json') == 'dat.json'
