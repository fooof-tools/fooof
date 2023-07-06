"""Tests for the fooof.data.conversions."""

from copy import deepcopy

import numpy as np

from fooof.core.modutils import safe_import
pd = safe_import('pandas')

from fooof.data.conversions import *

###################################################################################################
###################################################################################################

def test_model_to_dict(tresults, tbands):

    out = model_to_dict(tresults, peak_org=1)
    assert isinstance(out, dict)
    assert 'cf_0' in out
    assert out['cf_0'] == tresults.peak_params[0, 0]
    assert not 'cf_1' in out

    out = model_to_dict(tresults, peak_org=2)
    assert 'cf_0' in out
    assert 'cf_1' in out
    assert out['cf_1'] == tresults.peak_params[1, 0]

    out = model_to_dict(tresults, peak_org=3)
    assert 'cf_2' in out
    assert np.isnan(out['cf_2'])

    out = model_to_dict(tresults, peak_org=tbands)
    assert 'alpha_cf' in out

def test_model_to_dataframe(tresults, tbands, skip_if_no_pandas):

    for peak_org in [1, 2, 3]:
        out = model_to_dataframe(tresults, peak_org=peak_org)
        assert isinstance(out, pd.Series)

    out = model_to_dataframe(tresults, peak_org=tbands)
    assert isinstance(out, pd.Series)

def test_group_to_dataframe(tresults,  tbands, skip_if_no_pandas):

    fit_results = [deepcopy(tresults), deepcopy(tresults), deepcopy(tresults)]

    for peak_org in [1, 2, 3]:
        out = group_to_dataframe(fit_results, peak_org=peak_org)
        assert isinstance(out, pd.DataFrame)

    out = group_to_dataframe(fit_results, peak_org=tbands)
    assert isinstance(out, pd.DataFrame)
