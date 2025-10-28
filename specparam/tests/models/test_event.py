"""Tests for the specparam.models.event, including the event model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np

from specparam.models import SpectralGroupModel, SpectralTimeModel
from specparam.models.utils import compare_model_objs
from specparam.sim import sim_spectrogram
from specparam.modutils.dependencies import safe_import

pd = safe_import('pandas')

from specparam.tests.tsettings import TEST_DATA_PATH
from specparam.tests.tdata import default_group_params
from specparam.tests.tutils import plot_test

from specparam.models.event import *

###################################################################################################
###################################################################################################

def test_event_model():
    """Check event object initializes properly."""

    # Note: doesn't assert the object itself, which returns false empty
    fe = SpectralTimeEventModel(verbose=False)
    assert isinstance(fe, SpectralTimeEventModel)

def test_event_getitem(tfe):

    assert tfe.results[0]

def test_event_iter(tfe):

    for out in tfe.results:
        assert out

def test_event_n_properties(tfe):

    assert np.all(tfe.results.n_peaks)
    assert np.all(tfe.results.n_params)

def test_event_fit():

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())
    ys = [ys, ys]

    tfe = SpectralTimeEventModel(verbose=False)
    tfe.fit(xs, ys)
    results = tfe.results.get_results()
    assert results
    assert isinstance(results, dict)
    for key in results.keys():
        assert np.all(results[key])
        assert results[key].shape == (len(ys), n_windows)

def test_event_fit_par():
    """Test group fit, running in parallel."""

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())
    ys = [ys, ys]

    tfe = SpectralTimeEventModel(verbose=False)
    tfe.fit(xs, ys, n_jobs=2)
    results =  tfe.results.get_results()
    assert results
    assert isinstance(results, dict)
    for key in results.keys():
        assert np.all(results[key])
        assert results[key].shape == (len(ys), n_windows)

def test_event_print(tfe):

    tfe.print_results()

@plot_test
def test_event_plot(tfe, skip_if_no_mpl):

    tfe.plot()

def test_event_report(skip_if_no_mpl):

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())
    ys = [ys, ys]

    tfe = SpectralTimeEventModel(verbose=False)
    tfe.report(xs, ys)

    assert tfe

def test_event_load(tfe):

    # Test loading results
    ntfe = SpectralTimeEventModel(verbose=False)
    ntfe.load('test_event_res', TEST_DATA_PATH)
    assert ntfe.results.event_time_results

    # Test loading settings
    ntfe = SpectralTimeEventModel(verbose=False)
    ntfe.load('test_event_set', TEST_DATA_PATH)
    assert ntfe.algorithm.get_settings()

    # Test loading data
    ntfe = SpectralTimeEventModel(verbose=False)
    ntfe.load('test_event_dat', TEST_DATA_PATH)
    assert np.all(ntfe.data.spectrograms)

    # Test loading all elements
    ntfe = SpectralTimeEventModel(verbose=False)
    ntfe.load('test_event_all', TEST_DATA_PATH)
    assert compare_model_objs([tfe, ntfe], ['modes', 'settings', 'meta_data', 'bands', 'metrics'])

def test_event_get_model(tfe):

    # Check getting null model
    tfm_null = tfe.get_model()
    assert tfm_null
    # Check that settings are copied over properly, but data and results are empty
    assert tfe.algorithm.settings.values == tfm_null.algorithm.settings.values
    assert not tfm_null.data.has_data
    assert not tfm_null.results.has_model

    # Check without regenerating
    tfm0 = tfe.get_model(0, 0, False)
    assert tfm0
    assert tfm0.data.has_data
    assert tfm0.results.has_model

    # Check with regenerating
    tfm1 = tfe.get_model(1, 1, True)
    assert tfm1
    assert tfm1.data.has_data
    assert tfm1.results.has_model
    assert np.all(tfm1.results.model.modeled_spectrum)

def test_event_get_params(tfe):

    for component in tfe.modes.components:
        assert np.any(tfe.get_params(component))
        for pname in getattr(tfe.modes, component).params.labels:
            assert np.any(tfe.get_params(component, pname))

def test_event_get_group(tfe):

    ntfe0 = tfe.get_group(None, None)
    assert isinstance(ntfe0, SpectralTimeEventModel)

    einds = [0, 1]
    winds = [1, 2]
    n_out = len(einds) * len(winds)

    ntfe1 = tfe.get_group(einds, winds)
    assert isinstance(ntfe1, SpectralTimeEventModel)
    assert ntfe1.data.spectrograms.shape == (len(einds), len(tfe.data.freqs), len(winds))
    tkey = list(ntfe1.results.event_time_results.keys())[0]
    assert ntfe1.results.event_time_results[tkey].shape == (len(einds), len(winds))
    assert len(ntfe1.results.event_group_results), len(ntfe1.results.event_group_results[0]) == \
        (len(einds, len(winds)))

    # Test export sub-objects, including with None input
    ntft0 = tfe.get_group(None, None, 'time')
    assert isinstance(ntft0, SpectralTimeModel)
    assert not isinstance(ntft0, SpectralTimeEventModel)
    assert not ntft0.results.group_results

    ntft1 = tfe.get_group(einds, winds, 'time')
    assert isinstance(ntft1, SpectralTimeModel)
    assert not isinstance(ntft1, SpectralTimeEventModel)
    assert ntft1.results.group_results
    assert len(ntft1.results.group_results) == len(ntft1.data.power_spectra) == n_out

    ntfg0 = tfe.get_group(None, None, 'group')
    assert isinstance(ntfg0, SpectralGroupModel)
    assert not isinstance(ntfg0, (SpectralTimeModel, SpectralTimeEventModel))
    assert not ntfg0.results.group_results

    ntfg1 = tfe.get_group(einds, winds, 'group')
    assert isinstance(ntfg1, SpectralGroupModel)
    assert not isinstance(ntfg1, (SpectralTimeModel, SpectralTimeEventModel))
    assert ntfg1.results.group_results
    assert len(ntfg1.results.group_results) == len(ntfg1.data.power_spectra) == n_out

def test_event_drop():

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())
    ys = [ys, ys]
    tfe = SpectralTimeEventModel(verbose=False)
    tfe.fit(xs, ys)

    # Check list drops
    event_inds = [0]
    window_inds = [1]
    tfe.results.drop(event_inds, window_inds)
    assert len(tfe.results) == len(ys)
    dropped_fres = tfe.results.event_group_results[event_inds[0]][window_inds[0]]
    for field in [el for el in dropped_fres._fields if 'params' in el]:
        assert np.all(np.isnan(getattr(dropped_fres, field)))
    assert np.all(np.isnan(list(dropped_fres.metrics.values())))
    for key in tfe.results.event_time_results:
        assert np.isnan(tfe.results.event_time_results[key][event_inds[0], window_inds[0]])

    # Check dictionary drops
    drop_inds = {0 : [2], 1 : [1, 2]}
    tfe.results.drop(drop_inds)
    assert len(tfe.results) == len(ys)
    dropped_fres = tfe.results.event_group_results[0][drop_inds[0][0]]
    for field in [el for el in dropped_fres._fields if 'params' in el]:
        assert np.all(np.isnan(getattr(dropped_fres, field)))
    assert np.all(np.isnan(list(dropped_fres.metrics.values())))
    for key in tfe.results.event_time_results:
        assert np.isnan(tfe.results.event_time_results[key][0, drop_inds[0][0]])

def test_event_to_df(tfe, tbands, skip_if_no_pandas):

    df0 = tfe.to_df()
    assert isinstance(df0, pd.DataFrame)
    df1 = tfe.to_df(2)
    assert isinstance(df1, pd.DataFrame)
    df2 = tfe.to_df(tbands)
    assert isinstance(df2, pd.DataFrame)
