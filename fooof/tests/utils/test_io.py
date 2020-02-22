"""Test functions for fooof.utils.io."""

import numpy as np

from fooof.core.items import OBJ_DESC
from fooof.objs import FOOOF, FOOOFGroup

from fooof.tests.settings import TEST_DATA_PATH

from fooof.utils.io import *

###################################################################################################
###################################################################################################

def test_load_fooof():

    file_name = 'test_fooof_all'

    tfm = load_fooof(file_name, TEST_DATA_PATH)

    assert isinstance(tfm, FOOOF)

    # Check that all elements get loaded
    for result in OBJ_DESC['results']:
        assert not np.all(np.isnan(getattr(tfm, result)))
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is not None
    for data in OBJ_DESC['data']:
        assert getattr(tfm, data) is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm, meta_dat) is not None

def test_load_fooofgroup():

    file_name = 'test_fooofgroup_all'
    tfg = load_fooofgroup(file_name, TEST_DATA_PATH)

    assert isinstance(tfg, FOOOFGroup)

    # Check that all elements get loaded
    assert len(tfg.group_results) > 0
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) is not None
    assert tfg.power_spectra is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfg, meta_dat) is not None
