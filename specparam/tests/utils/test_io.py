"""Test functions for specparam.utils.io."""

import numpy as np

from specparam.core.items import OBJ_DESC

from specparam.objs import (SpectralModel, SpectralGroupModel,
                            SpectralTimeModel, SpectralTimeEventModel)

from specparam.tests.tsettings import TEST_DATA_PATH

from specparam.utils.io import *

###################################################################################################
###################################################################################################

def test_load_model():

    file_name = 'test_model_all'

    tfm = load_model(file_name, TEST_DATA_PATH)

    assert isinstance(tfm, SpectralModel)

    # Check that all elements get loaded
    for result in OBJ_DESC['results']:
        assert not np.all(np.isnan(getattr(tfm, result)))
    for setting in OBJ_DESC['settings']:
        assert getattr(tfm, setting) is not None
    for data in OBJ_DESC['data']:
        assert getattr(tfm, data) is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfm, meta_dat) is not None

def test_load_group_model():

    file_name = 'test_group_all'
    tfg = load_group_model(file_name, TEST_DATA_PATH)

    assert isinstance(tfg, SpectralGroupModel)

    # Check that all elements get loaded
    assert len(tfg.group_results) > 0
    for setting in OBJ_DESC['settings']:
        assert getattr(tfg, setting) is not None
    assert tfg.power_spectra is not None
    for meta_dat in OBJ_DESC['meta_data']:
        assert getattr(tfg, meta_dat) is not None

def test_load_time_model(tbands):

    file_name = 'test_time_all'

    # Load without bands definition
    tft = load_time_model(file_name, TEST_DATA_PATH)
    assert isinstance(tft, SpectralTimeModel)

    # Load with bands definition
    tft2 = load_time_model(file_name, TEST_DATA_PATH, tbands)
    assert isinstance(tft2, SpectralTimeModel)
    assert tft2.time_results

def test_load_event_model(tbands):

    file_name = 'test_event_all'

    # Load without bands definition
    tfe = load_event_model(file_name, TEST_DATA_PATH)
    assert isinstance(tfe, SpectralTimeEventModel)
    assert len(tfe) > 1

    # Load with bands definition
    tfe2 = load_event_model(file_name, TEST_DATA_PATH, tbands)
    assert isinstance(tfe2, SpectralTimeEventModel)
    assert tfe2.event_time_results
    assert len(tfe2) > 1
