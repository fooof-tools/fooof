"""Tests for the specparam.objs.event, including the event model object and it's methods.

NOTES
-----
The tests here are not strong tests for accuracy.
They serve rather as 'smoke tests', for if anything fails completely.
"""

import numpy as np

from specparam.sim import sim_spectrogram
from specparam.core.modutils import safe_import

pd = safe_import('pandas')

from specparam.tests.settings import TEST_DATA_PATH
from specparam.tests.tutils import default_group_params, plot_test

from specparam.objs.event import *

###################################################################################################
###################################################################################################

def test_event_model():
    """Check event object initializes properly."""

    # Note: doesn't assert the object itself, which returns false empty
    fe = SpectralTimeEventModel(verbose=False)
    assert isinstance(fe, SpectralTimeEventModel)

def test_event_getitem(tft):

    assert tft[0]

def test_event_iter(tfe):

    for out in tfe:
        assert out

def test_event_n_peaks(tfe):

    assert np.all(tfe.n_peaks_)

def test_event_fit():

    n_windows = 3
    xs, ys = sim_spectrogram(n_windows, *default_group_params())
    ys = [ys, ys]

    tfe = SpectralTimeEventModel(verbose=False)
    tfe.fit(xs, ys)

    results = tfe.get_results()

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

def test_event_get_model(tfe):

    # Check without regenerating
    tfm0 = tfe.get_model(0, 0, False)
    assert tfm0

    # Check with regenerating
    tfm1 = tfe.get_model(1, 1, True)
    assert tfm1
    assert np.all(tfm1.modeled_spectrum_)

def test_event_get_params(tfe):

    for dname in ['aperiodic', 'peak', 'error', 'r_squared']:
        assert np.any(tfe.get_params(dname))

def test_event_get_group(tfe):

    ntfe = tfe.get_group([0], [1, 2])
    assert ntfe

def test_event_to_df(tfe, tbands, skip_if_no_pandas):

    df0 = tfe.to_df()
    assert isinstance(df0, pd.DataFrame)
    df1 = tfe.to_df(2)
    assert isinstance(df1, pd.DataFrame)
    df2 = tfe.to_df(tbands)
    assert isinstance(df2, pd.DataFrame)
